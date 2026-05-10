import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'data/app_data_store.dart';
import 'data/asset_data_loader.dart';
import 'data/hot_update_service.dart';
import 'pages/tree_timeline_page.dart';
import 'theme/app_theme.dart';

void main() {
  HotUpdateService.installCertOverride();
  runApp(const WzxHistoryApp());
}

class WzxHistoryApp extends StatelessWidget {
  const WzxHistoryApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) {
        final hot = HotUpdateService();
        final loader = AssetDataLoader(hotUpdate: hot);
        final c = AppDataController(hotUpdate: hot);
        // Bootstrap: pull data, then load. Hot sync runs in parallel with
        // first-paint of bundled data so cold start stays fast.
        loader.loadAll().then(
          (loaded) => c.setStore(AppDataStore.fromLoaded(loaded)),
          onError: c.setError,
        );
        // Try remote sync; if anything new, reload data afterwards.
        hot.syncData().then((changed) async {
          if (changed) {
            try {
              final reloaded = await loader.loadAll();
              c.setStore(AppDataStore.fromLoaded(reloaded));
            } catch (_) {
              // Keep current store on reload error.
            }
          }
        });
        return c;
      },
      child: MaterialApp(
        title: '王子学历史',
        debugShowCheckedModeBanner: false,
        themeMode: ThemeMode.system,
        theme: AppTheme.light(),
        darkTheme: AppTheme.dark(),
        home: const _Bootstrap(),
      ),
    );
  }
}

class _Bootstrap extends StatelessWidget {
  const _Bootstrap();

  @override
  Widget build(BuildContext context) {
    final ctrl = context.watch<AppDataController>();
    if (ctrl.error != null) {
      return Scaffold(
        appBar: AppBar(title: const Text('数据加载失败')),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Text('错误:\n${ctrl.error}',
                style: Theme.of(context).textTheme.bodyMedium),
          ),
        ),
      );
    }
    if (!ctrl.isReady) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }
    return const TreeTimelinePage();
  }
}
