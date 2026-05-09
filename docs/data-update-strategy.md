# 数据热更新策略

> 创建于 2026-05。**Phase 1.5 模块设计文档**。
> 让 app 二进制不变,数据从云端拉取 — push GitHub commit 即更新朋友的 app。

---

## 设计目标

```
   开发期(你的电脑)              运行期(朋友的手机)
   ┌──────────────────────┐      ┌──────────────────────┐
   │ git push 新数据       │      │ app 启动              │
   │  ↓                   │      │  ↓                   │
   │ GitHub commit         │ ──→  │ 后台拉 manifest      │
   │  ↓                   │      │  ↓                   │
   │ raw.githubusercontent │      │ hash 变 → 下载       │
   │ 立即可访问            │      │  ↓                   │
   └──────────────────────┘      │ 写入本地 cache       │
                                  │  ↓                   │
                                  │ 下次启动用新数据       │
                                  └──────────────────────┘

   核心收益:
   • 朋友只装一次 APK,以后内容自动更新
   • 你 push 一次 GitHub commit 就完事(没有 release 流程)
   • app 二进制不变,审核 / 签名 / 兼容性问题归零
```

---

## 为什么不做代码热更

Flutter 的代码热更**几乎不可行**:

```
   平台          代码热更可行性    备注
   ────────     ──────────────    ─────────────────────────
   iOS          ✗ 完全禁止         App Store 政策禁止动态执行
   Android      △ 麻烦             SO 注入 / Java 热修复都重
   方案         CodePush 类        Flutter 没有官方支持
                Shorebird          需要付费(~$20/月)
```

**结论**: 只做数据热更,代码改动通过新 APK 推送(频率应很低,~每月一次)。

---

## 选型: GitHub Raw vs Cloudflare R2

```
   方面             GitHub Raw                Cloudflare R2
   ───────────     ─────────────────────     ──────────────────
   成本             免费                       免费 (10GB / 月 1M 请求)
   速度 (海外)      快                          快
   速度 (中国大陆)  **慢/不稳定** (墙)         **快**
   配置             0(已有 GitHub 仓库)        ~5 分钟
   CDN              基础                       全球
   流量限制         soft(滥用会限)              10GB/月免费
   仓库需公开?      是(公开仓库的 raw)         否
   适合朋友群       海外 / 你自己              中国大陆为主

   推荐路径:
   • Phase 1 先用 GitHub Raw(0 配置,验证流程)
   • 若大陆朋友抱怨慢 → 切到 R2
   • 切换只需改 Flutter 端的 BASE_URL,数据格式不变
```

---

## manifest.json 格式

```
   assets/data/manifest.json
   ────────────────────────────────────────
   {
     "_schemaVersion": "v0.6",
     "_generated": "2026-05-09T17:30:00+08:00",
     "_minAppVersion": "1.0.0",
     "files": {
       "dynasties.json":  {"hash": "sha256:abcd1234...", "size": 12345},
       "regimes.json":    {"hash": "sha256:ef567890...", "size": 23456},
       "events.json":     {"hash": "sha256:9876fedc...", "size": 1234567},
       "persons.json":    {"hash": "sha256:cafebabe...", "size": 234567}
     }
   }
```

`_schemaVersion`: 必须和 app 内置支持的版本兼容(major.minor 相同)。
`_minAppVersion`: app 版本 < 此值则提示用户升级 APK。
`hash`: SHA-256 of file content,用于变更检测。
`size`: 字节,用于显示下载进度。

---

## Flutter 端 RemoteDataSyncService

```dart
class RemoteDataSyncService {
  static const String BASE_URL =
      "https://raw.githubusercontent.com/USER/REPO/main/assets/data/";

  /// 启动时调用,后台异步执行(不阻塞 UI)
  Future<void> syncIfNeeded() async {
    try {
      final remoteManifest = await _fetchManifest();
      final localManifest = await _readLocalManifest();

      // 1. schema 版本检查
      if (!_isCompatible(remoteManifest._schemaVersion)) {
        _notifyUserUpgradeApp();
        return;
      }

      // 2. 比对 hash,下载变化的文件
      for (final entry in remoteManifest.files.entries) {
        if (localManifest?.files[entry.key]?.hash != entry.value.hash) {
          await _downloadFile(entry.key);
        }
      }

      // 3. 更新本地 manifest
      await _saveManifest(remoteManifest);
    } catch (_) {
      // 网络错误等 — 沉默失败,继续用旧数据
    }
  }
}
```

**特性**:
- 后台异步,不阻塞当前会话
- 失败静默(墙 / 离线 / 朋友机场关网),用户不感知
- 下次启动生效(避免会话中数据突变)
- schema 不兼容主动提示

---

## 加载流程(全图)

```
                  app 启动
                     │
                     ▼
            ┌─────────────────────┐
            │ DataRepository.init  │
            └─────────┬───────────┘
                     │
            ┌────────┴────────┐
            ▼                 ▼
   有 cache?            没 cache?
            │                 │
            ▼                 ▼
   读 cache              读 assets/data/(内置)
            │                 │
            └────────┬────────┘
                     ▼
            ┌─────────────────────┐
            │ UI 显示树图           │  ← 用户已经看到内容
            └─────────┬───────────┘
                     │
                后台并发
                     ▼
            ┌─────────────────────┐
            │ RemoteDataSyncService│
            └─────────┬───────────┘
                     │
            ┌────────┴────────┐
            ▼                 ▼
   网络 OK + hash 不同      其他
            │                 │
            ▼                 ▼
   下载新文件 → 写 cache   静默退出
            │
            ▼
   下次启动用新数据
```

---

## 边界情况处理

```
   场景                       处理
   ────────────────────       ────────────────────────────
   离线启动                    用 cache 或 assets,正常运行
   首次启动 + 有网            从 assets 显示,后台拉 cache
   首次启动 + 离线            用 assets,等下次有网再更新
   manifest hash 全相同        无下载,日志记一笔
   下载途中网络断              partial 文件丢弃,下次重试
   schema 不兼容 (major)      弹"请升级 APK"提示,不更新
   cache 文件损坏 (parse fail) 删 cache 改用 assets,重新下载
   GitHub Raw 限流            sleep 1 小时再试
```

---

## 部署流程(你的视角)

```
   1. 在 data_source/ 改了某个朝代的事件
   2. python tools/validate.py    # 校验通过
   3. python tools/build.py       # 产出 assets/data/*.json + 新 manifest
   4. git add assets/data/ data_source/
   5. git commit -m "data: 西周事件补全"
   6. git push origin main
   7. 完成 — 朋友打开 app 自动看到新内容

   没有 release 流程,没有版本号,没有审核
```

---

## 关于隐私 / 流量

- app 启动时**只**拉 manifest.json (~几 KB)
- 仅在 hash 不同时才下载具体文件
- 不发送任何用户标识(纯 GET 请求)
- 一年下来朋友的流量消耗 ~10-50 MB(数据增量推送)

---

## 升级路径(若 Phase 后期需要)

- v1 (Phase 1): GitHub Raw,全量替换
- v2 (Phase 后期,若需要): 增量更新(每个朝代独立 hash + 单独下载)
- v3 (若做大): 切到 R2 / 国内 OSS,提速

每次升级**保持 manifest.json 格式向后兼容**,旧版 app 仍可工作。

---

## 安全考虑

- HTTPS 强制(GitHub Raw 默认 HTTPS)
- hash 校验防中间人篡改: app 比较下载文件 SHA-256 与 manifest 中的 hash,不一致丢弃
- 不下载可执行代码 — 只下载 JSON,Flutter 端解析,无 RCE 风险

---

## Phase 1.5 任务清单

详见 `phase-1-data-source-spike` change 完成后的下一个 change(可能命名
`phase-1-data-hot-update`)。粗略:

- [ ] tools/build_manifest.py — 生成 manifest.json
- [ ] tools/build.py 集成 — build 时自动更新 manifest
- [ ] Flutter: DataRepository 支持 cache + assets 两层 fallback
- [ ] Flutter: RemoteDataSyncService 实现
- [ ] schema version 检查 + 升级提示 UI
- [ ] 真机测试(联网 / 离线 / 慢网络场景)
