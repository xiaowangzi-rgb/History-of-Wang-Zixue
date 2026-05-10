"""Append commonly-known historical events that our coverage was missing.

All summaries are original — no copy from any source. Phrasing follows
docs/content-style-guide.md A风格 (textbook-tone, 100-200 chars).
"""
import json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EV = ROOT / "data_source" / "events"


def E(eid, name, year, dyn, cat, summary, *, regime=None, hist="historical", uncertain="year"):
    rec = {
        "id": f"event_{eid}",
        "name": name,
        "year": year,
        "dynastyId": f"dynasty_{dyn}",
        "category": cat,
        "summary": summary,
        "historicity": hist,
        "yearUncertainty": uncertain,
        "_schemaVersion": "v0.6",
        "source": "manual",
    }
    if regime:
        rec["regimeId"] = f"regime_{regime}"
    return rec


# Tuples of (file_short, [events to append])
ADDITIONS = {
    "legendary": [
        E("legendary_pangu", "盘古开天辟地", -3000, "legendary", "religion",
          "传说中混沌初开,盘古以巨斧劈开天地,清气上升为天,浊气下沉为地。盘古身死后,身体化作日月山川,中华神话宇宙创生由此始。",
          hist="legendary", uncertain="era"),
        E("legendary_nuwa", "女娲补天 抟土造人", -2900, "legendary", "religion",
          "传说女娲炼五色石以补苍天,断鳌足以立四极,抟黄土造人。中华民族始祖神之一,与伏羲并列为人文之源。",
          hist="legendary", uncertain="era"),
        E("legendary_youchao", "有巢氏构木为巢", -2800, "legendary", "science",
          "传说远古有巢氏教民构木为屋以避禽兽虫蛇之害,开启从穴居向房屋的文明转折。",
          hist="legendary", uncertain="era"),
        E("legendary_suiren", "燧人氏钻木取火", -2700, "legendary", "science",
          "传说燧人氏观鸟啄燧木生烟而悟,发明钻木取火之法。中华民族用火文明的起点。",
          hist="legendary", uncertain="era"),
        E("legendary_fuxi", "伏羲画八卦 教民结网", -2600, "legendary", "culture",
          "传说伏羲氏观天地之象画八卦,教民结网捕鱼、定姓氏、立婚姻。被尊为中华人文始祖。",
          hist="legendary", uncertain="era"),
        E("legendary_shennong", "神农尝百草", -2700, "legendary", "science",
          "传说炎帝神农氏尝百草以辨药性,著《神农本草经》之肇始。又教民耕种五谷,故称\"神农\"。",
          hist="legendary", uncertain="era"),
    ],

    "qin.json": [],  # below; we'll register by exact filename

    "eastern_zhou": [
        # Spring-autumn classics
        E("ez_guanbao", "管鲍之交", -680, "eastern_zhou", "person",
          "管仲与鲍叔牙相识,鲍叔牙明知管仲家贫多取却不计较。后管仲落难,鲍叔牙力荐其为齐桓公相,自处其下。\"生我者父母,知我者鲍子\",成知己典范。",
          regime="qi_state_sa"),
        E("ez_qihuan_jiuhe", "齐桓公九合诸侯", -651, "eastern_zhou", "diplomacy",
          "齐桓公在管仲辅佐下,以\"尊王攘夷\"号召诸侯,葵丘之盟主持九次会盟。春秋首霸地位由此确立,中原秩序得以维持百年。",
          regime="qi_state_sa"),
        E("ez_zhonger_exile", "晋公子重耳流亡十九年", -636, "eastern_zhou", "person",
          "晋献公骊姬之乱后,公子重耳流亡狄、卫、齐、楚等八国十九年,得多位君主礼遇。归国即位即晋文公,成春秋第二霸主。",
          regime="jin_state_sa"),
        E("ez_chu_zhuangwang_yiming", "楚庄王一鸣惊人", -613, "eastern_zhou", "person",
          "楚庄王即位三年沉湎声色不出政令,大臣讽以鸟喻\"三年不鸣\"。庄王曰\"不鸣则已,一鸣惊人\",自此整顿朝纲,问鼎中原。",
          regime="chu_state_sa"),
        E("ez_jiatu_miyi", "晋献公假途灭虢", -658, "eastern_zhou", "war",
          "晋献公以名马美玉贿虞君借道伐虢,得手后回师灭虞。\"唇亡齿寒\"成语典出宫之奇谏虞君之言,被忽视致亡。",
          regime="jin_state_sa"),
        E("ez_xiangao_lao", "弦高犒师智退秦军", -627, "eastern_zhou", "war",
          "郑国商人弦高于路上遇秦军袭郑,假托国君之命献十二头牛犒劳秦军,使秦军以为郑有备而退。一介商人挽国于危。"),
        E("ez_xiao_battle", "晋楚崤之战 秦军全军覆没", -627, "eastern_zhou", "war",
          "秦军远袭郑国不成,归途经崤山遭晋军伏击,三帅被俘,秦军覆没。秦东进受阻,转而经营西方戎狄。",
          regime="jin_state_sa"),
        E("ez_qilu_changshao", "齐鲁长勺之战 一鼓作气", -684, "eastern_zhou", "war",
          "齐鲁长勺交战,鲁庄公欲先击,曹刿止之曰\"一鼓作气,再而衰,三而竭\"。待齐三鼓后鲁军反击大胜。\"一鼓作气\"成语典出于此。",
          regime="lu"),
        E("ez_yanzi_chu", "晏子使楚 不辱使命", -540, "eastern_zhou", "diplomacy",
          "齐相晏子身材矮小,出使楚国时楚王屡欲羞辱,晏子以\"使狗国者从狗门入\"\"橘生淮南则为橘\"等机智应对,捍卫齐国尊严。",
          regime="qi_state_sa"),
        E("ez_zichan_reform", "子产改革 铸刑书于鼎", -536, "eastern_zhou", "politics",
          "郑国执政子产铸成文法于刑鼎,公开法律。挑战\"刑不上大夫\"传统,法家\"以法治国\"先声。"),
        E("ez_wuzixu", "伍子胥过昭关 一夜白头", -522, "eastern_zhou", "person",
          "楚平王杀伍奢全家,其子伍子胥逃亡过昭关,愁苦一夜须发尽白。后入吴助阖闾灭楚,鞭楚平王尸三百以报父仇。",
          regime="wu_state"),
        E("ez_konguzi_lunyu", "孔门弟子 编订《论语》", -490, "eastern_zhou", "culture",
          "孔子弟子三千、贤人七十二。子贡、子路、颜回、曾参、子夏等各有专长。孔子卒后弟子辑师徒言行成《论语》,儒家圣典自此立。",
          regime="lu"),
        E("ez_mozi", "墨子创墨家 兼爱非攻", -440, "eastern_zhou", "culture",
          "宋人墨翟反对儒家差等之爱,主张\"兼爱\"\"非攻\"\"尚贤\"\"节用\"。墨家与儒家并称战国\"显学\",门徒严密如军事组织。"),
        E("ez_bian_que", "扁鹊望诊 四诊法立", -400, "eastern_zhou", "science",
          "渤海郡神医秦越人,世称扁鹊。创望、闻、问、切四诊法,精通内外妇儿各科。\"扁鹊见蔡桓公\"故事流传至今。",
          regime="qi_state_sa"),
        E("ez_libing_dujiangyan", "李冰修建都江堰", -256, "eastern_zhou", "science",
          "蜀郡守李冰父子主持修建都江堰水利工程,以鱼嘴分水、飞沙堰排洪、宝瓶口引水。两千余年来岷江水患平息,成都平原沃野千里。",
          regime="qin_state"),
        E("ez_ximen_bao", "西门豹治邺 破河伯娶妇", -422, "eastern_zhou", "politics",
          "魏文侯任西门豹为邺令,破除\"河伯娶妇\"巫术,惩巫祝豪绅,凿十二渠引漳水溉田。法家政治家典范。",
          regime="wei_state"),
        E("ez_wanbi_guizhao", "完璧归赵 蔺相如使秦", -283, "eastern_zhou", "diplomacy",
          "秦昭王欲以十五城换赵和氏璧,蔺相如奉璧入秦,识破诈骗,巧使璧归赵国。\"完璧归赵\"成语典出于此。",
          regime="zhao"),
        E("ez_fujing_qingzui", "负荆请罪 将相和", -279, "eastern_zhou", "person",
          "赵将廉颇不服蔺相如位居其上,屡欲辱之。相如避让,廉颇闻其\"先国家后私仇\"之言,负荆登门请罪。\"将相和\"成佳话。",
          regime="zhao"),
        E("ez_zhao_kuo", "赵括纸上谈兵 长平惨败", -260, "eastern_zhou", "war",
          "赵孝成王以赵括代廉颇,赵括熟读兵书但无实战经验,贸然出击。秦将白起诱敌深入,围困赵军四十六日。\"纸上谈兵\"成语永警后世。",
          regime="zhao"),
        E("ez_xinlingjun", "信陵君窃符救赵", -257, "eastern_zhou", "war",
          "魏公子无忌窃魏王虎符调魏军,逼老将晋鄙交权,率军救赵破秦。\"窃符救赵\"信陵君义气千秋,为战国四公子之首。",
          regime="wei_state"),
        E("ez_maosui", "毛遂自荐 平原君赴楚", -257, "eastern_zhou", "person",
          "赵平原君欲选二十门客赴楚求救,差一人。毛遂自请,初被嘲未得用,殿前持剑迫楚王歃血定盟。\"毛遂自荐\"\"脱颖而出\"成语并出。",
          regime="zhao"),
        E("ez_zhaowuling", "赵武灵王胡服骑射", -307, "eastern_zhou", "politics",
          "赵武灵王为强国,改赵军戎装为胡人短装,弃车战行骑射。冲破\"夷夏之防\",军事改革开中原以胡制胡先河。",
          regime="zhao"),
        E("ez_tiandanmoji", "田单火牛阵 复国齐", -279, "eastern_zhou", "war",
          "齐被燕乐毅几灭,只剩即墨、莒。田单守即墨,以千余牛角缚刀、尾束苇灌油点燃夜冲燕营。一战复齐七十余城,齐由此中兴。",
          regime="qi"),
        E("ez_fanli_yinwei", "范蠡功成身退 经商致富", -473, "eastern_zhou", "person",
          "助勾践灭吴后,范蠡识勾践\"可与共患难,不可与共安乐\",泛舟太湖远遁齐国。后三聚千金、三散家财,世称\"陶朱公\",中国商圣。"),
        E("ez_fanju_yuanjiao", "范雎远交近攻", -270, "eastern_zhou", "politics",
          "魏人范雎入秦,献\"远交近攻\"之策:与远国结盟、攻打近国。秦昭王采纳,蚕食三晋,为秦统一战略奠基。",
          regime="qin_state"),
        E("ez_chutong_taihou", "触龙说赵太后", -265, "eastern_zhou", "diplomacy",
          "秦攻赵急,赵向齐求救,齐索长安君为质。赵太后不许,左师触龙以\"父母之爱子,则为之计深远\"婉言相劝,太后释然送质。",
          regime="zhao"),
        E("ez_zoji_jianqi", "邹忌讽齐王纳谏", -354, "eastern_zhou", "politics",
          "齐相邹忌以与城北徐公比美的家事,讽齐威王\"宫妇左右莫不私王\"。威王下令\"群臣吏民,能面刺寡人之过者赐上赏\",齐国大治。",
          regime="qi"),
        E("ez_mengzi_mu", "孟母三迁 断织教子", -350, "eastern_zhou", "person",
          "孟母仉氏为给孟子良好成长环境,三次搬家:由墓地至市集再至学宫旁。又见孟子逃学,断织以告\"学如织,半途而废前功尽弃\"。",
          regime="lu"),
        E("ez_wuqi", "吴起变法 楚国强盛", -382, "eastern_zhou", "politics",
          "卫人吴起,初为鲁、魏将立功无数。后入楚为令尹,变法富国强兵,得罪贵族。楚悼王死,吴起伏王尸被乱箭射死,变法亦废。",
          regime="chu"),
    ],

    "qin": [
        E("qin_zhang_liang", "张良博浪沙刺秦", -218, "qin", "war",
          "韩国贵族后裔张良为报国仇,以重金募力士铸百二十斤大铁锥,伏击秦始皇于博浪沙。误中副车,始皇大索十日不得。"),
        E("qin_xiang_yu_pofuzhouzhou", "项羽破釜沉舟 巨鹿之战", -207, "qin", "war",
          "秦军围赵于巨鹿,项羽率楚军救援,渡河后凿沉船只、砸碎炊釜。九战九捷,大破秦将王离主力。\"破釜沉舟\"成语典出于此。"),
        E("qin_xiao_he_zhuihan", "萧何月下追韩信", -206, "qin", "person",
          "韩信不被刘邦重用,叛逃。萧何闻之不及报告,亲自月夜追还。说服刘邦拜为大将军。\"萧何月下追韩信\"成中国君臣相得佳话。"),
        E("qin_zhao_gao_lumawei", "赵高指鹿为马", -207, "qin", "politics",
          "秦二世胡亥时,丞相赵高欲试朝臣,献鹿称马。称鹿者皆被构陷处死。\"指鹿为马\"成奸佞试探之典。"),
        E("qin_hongmen", "鸿门宴 项庄舞剑", -206, "qin", "war",
          "项羽设宴鸿门,本欲杀刘邦。范增数次以玉玦示意,项庄起舞欲剑刺,项伯起舞掩护刘邦。樊哙闯帐,刘邦借如厕之机逃生。"),
        E("qin_chu_han_zhengba", "楚汉相争 四年决战", -206, "qin", "war",
          "项羽自封西楚霸王,封刘邦为汉王。刘邦明修栈道暗度陈仓,联韩信、彭越、英布,与项羽决战四年。垓下之围楚歌四起,项羽乌江自刎。"),
    ],

    "western_han": [
        E("xh_xiao_he_san_jie", "萧规曹随", -193, "western_han", "politics",
          "汉初萧何制定律法治理天下,卒后曹参继任。曹参\"举事无所变更,一遵萧何约束\",汉初黄老无为之治得以延续。"),
        E("xh_su_wu_muyang", "苏武北海牧羊", -100, "western_han", "diplomacy",
          "汉武帝遣苏武使匈奴,被扣留。匈奴胁降不从,流放北海(贝加尔湖)牧公羊,云\"羝乳乃得归\"。十九年持节不屈,昭帝时归汉。"),
        E("xh_zhaojun", "昭君出塞 和亲匈奴", -33, "western_han", "diplomacy",
          "汉元帝以宫女王昭君嫁匈奴呼韩邪单于。昭君之美据传\"落雁\",和亲后汉匈五十年无战事。中国四大美人之一。"),
        E("xh_li_guang", "飞将军李广 匈奴丧胆", -119, "western_han", "war",
          "李广善骑射,与匈奴大小七十余战,匈奴号\"飞将军\",数年不敢入境。然命运多舛,终未封侯。\"冯唐易老,李广难封\"。"),
        E("xh_huo_guang", "霍光辅政 废立皇帝", -87, "western_han", "politics",
          "汉武帝临终托孤霍光,辅佐昭帝、废昌邑王、立宣帝。前后专政二十年。死后家族谋反被诛,但其辅政功绩被列为\"麒麟阁十一功臣\"之首。"),
        E("xh_tiying", "缇萦救父 废肉刑", -167, "western_han", "politics",
          "齐太仓令淳于意获罪当受肉刑,小女缇萦上书汉文帝愿没身为奴赎父罪。文帝感动,下诏废除黥、劓、刖三种肉刑。"),
        E("xh_baideng", "白登之围 汉匈和亲", -200, "western_han", "war",
          "汉高祖刘邦亲率三十万军伐匈奴,被冒顿单于围困白登山七日。陈平献计贿冒顿阏氏方解围。汉初被迫行和亲政策七十年。"),
        E("xh_han_xin_si", "韩信被诛 兔死狗烹", -196, "western_han", "person",
          "汉初三杰之一韩信,功高震主。先被改封楚王,后贬淮阴侯,终被吕后诱入未央宫缢杀。\"成也萧何,败也萧何\"\"鸟尽弓藏\"皆出于此。"),
        E("xh_kunyang", "昆阳之战 王莽败亡前夜", 23, "western_han", "war",
          "新莽末年绿林军起义,王莽派四十二万大军围昆阳。刘秀率三千精骑突袭中军,大破王莽主力。新朝从此一蹶不振。"),
        E("xh_yan_tie_huiyi", "盐铁会议 汉廷大辩论", -81, "western_han", "economy",
          "汉昭帝召贤良文学六十余人与丞相、御史大夫论盐铁酒榷专卖政策。儒法两派激辩国家干预经济利弊,桓宽辑为《盐铁论》,千古经济论战。"),
    ],

    "eastern_han": [
        E("eh_san_gu", "刘备三顾茅庐 隆中对", 207, "eastern_han", "person",
          "刘备屯新野,徐庶荐诸葛亮。三顾茅庐于隆中,孔明献\"占荆益、联孙吴、抗曹操\"三分天下之策。蜀汉立国之纲领由此而出。"),
        E("eh_caowei_jiu", "曹操煮酒论英雄", 199, "eastern_han", "person",
          "曹操邀刘备煮酒,论天下英雄,曰\"今天下英雄,惟使君与操耳\"。刘备闻言失箸,适天惊雷,借此遮饰。后世传为韬晦经典。"),
        E("eh_lvmeng", "吕蒙白衣渡江 袭荆州", 219, "eastern_han", "war",
          "孙权令吕蒙取荆州,蒙佯病归建业,使陆逊代任示弱关羽。后率精兵伪装商人白衣渡江,袭取江陵。关羽北伐功败垂成,败走麦城。"),
        E("eh_guan_yu_shui", "关羽水淹七军 威震华夏", 219, "eastern_han", "war",
          "关羽北伐攻襄樊,擒于禁、斩庞德。利用秋雨连绵,决堤水淹曹军七军三万余人。\"威震华夏\",曹操几欲迁都避其锋。"),
        E("eh_dong_zhuo_wang_yun", "王允施美人计 吕布杀董卓", 192, "eastern_han", "war",
          "司徒王允痛恨董卓乱政,以养女貂蝉离间董卓与吕布。吕布于未央宫戟刺董卓,百姓欢腾起舞。然李傕郭汜旋即反扑,长安再陷战乱。"),
        E("eh_ban_chao_tou_bi", "班超投笔从戎", 73, "eastern_han", "diplomacy",
          "班超本为兰台令史,叹\"大丈夫无他志略,犹当效傅介子、张骞立功异域\",投笔从戎西使。三十一年间定西域五十余国,封定远侯。"),
        E("eh_handi_qiufo", "汉明帝天竺求佛", 67, "eastern_han", "religion",
          "汉明帝梦金人飞行,询臣以为佛。遣使迎天竺高僧迦叶摩腾、竺法兰至洛阳,以白马驮经,建白马寺译《四十二章经》。佛教正式入华。"),
        E("eh_ma_yuan", "马援老当益壮 马革裹尸", 49, "eastern_han", "war",
          "光武帝时名将马援,六十二岁仍请战南征。\"丈夫为志,穷当益坚,老当益壮\"\"马革裹尸,何足道哉\"皆出于他。终病死军中。"),
    ],

    "three_kingdoms": [
        E("3k_qiqin_menghuo", "诸葛亮七擒孟获", 225, "three_kingdoms", "war",
          "蜀建兴三年,诸葛亮南征平定南中四郡。对叛乱首领孟获七擒七纵,使其心悦诚服。\"攻心为上,攻城为下\"成中国战略名言。",
          regime="shu"),
        E("3k_huoshao_lianying", "陆逊火烧连营七百里", 222, "three_kingdoms", "war",
          "夷陵之战,陆逊以逸待劳,见蜀军七百里连营在山林立寨,趁东南风发动火攻。刘备大败退白帝城。\"连营七百里,可烧\"成笑话。",
          regime="wu"),
        E("3k_simayi_zhuangbing", "司马懿装病 高平陵之变", 249, "three_kingdoms", "politics",
          "司马懿装病避曹爽锋芒。曹爽兄弟离都谒陵之机,司马懿勒兵奉皇太后令关闭洛阳城门,夺曹爽兵权,夷其三族。司马氏自此专魏权。",
          regime="wei"),
        E("3k_dengai_yinping", "邓艾偷渡阴平 蜀汉亡", 263, "three_kingdoms", "war",
          "钟会主力被姜维阻于剑阁,邓艾率精兵偷渡阴平七百里无人之地,以毡裹身滚下悬崖。直取成都,刘禅出降。蜀汉亡。",
          regime="shu"),
        E("3k_lechan_busi_shu", "刘禅乐不思蜀", 264, "three_kingdoms", "person",
          "蜀亡后,刘禅入洛阳被封安乐公。司马昭设宴奏蜀乐,蜀旧臣皆涕泣,禅嬉笑自若。问\"思蜀否\"答\"此间乐,不思蜀\"。",
          regime="shu"),
    ],

    "western_jin": [
        E("wj_shichong_doufu", "石崇王恺斗富 西晋奢风", 290, "western_jin", "economy",
          "西晋外戚王恺与富豪石崇斗富,以蜡烛代柴煮饭、紫丝为屏,武帝亦助王恺。石崇击碎武帝所赐二尺珊瑚以六七尺者偿之。西晋奢靡之风可见。"),
    ],

    "eastern_jin": [
        E("ej_shi_le_dushu", "石勒爱才 重视读书人", 320, "eastern_jin", "person",
          "羯族奴隶出身的后赵开国皇帝石勒,虽不识字却令人读《汉书》,常令人读《史记》。听到郦食其劝刘邦立六国后人时叹\"此法当败\"。",
          regime="shu"),
        E("ej_wang_xizhi", "书圣王羲之 鹅池换帖", 360, "eastern_jin", "culture",
          "王羲之爱鹅,曾为山阴道士书《黄庭经》换鹅。其书法\"飘若浮云,矫若惊龙\",《兰亭序》《快雪时晴帖》流传千年。子王献之并称\"二王\"。"),
        E("ej_xie_an", "谢安东山再起 淝水从容", 383, "eastern_jin", "person",
          "谢安隐居东山二十余载,四十始仕。前秦百万压境,与客围棋如常。淝水之战大捷,捷报至时神色不变,弈罢内宅过门折屐齿而不觉。"),
        E("ej_huan_wen", "桓温三次北伐", 354, "eastern_jin", "war",
          "权臣桓温三次北伐前秦、姚襄、前燕,所向有功。曰\"既不能流芳百世,亦不足复遗臭万载耶\"。后欲篡位未果,病卒。"),
    ],

    "southern_northern": [
        E("sn_chenhouzhu", "陈后主玉树后庭花 国亡", 589, "southern_northern", "culture",
          "陈后主陈叔宝荒淫无度,作《玉树后庭花》艳曲,与宠妃夜夜笙歌。隋兵渡江,陈后主与张丽华、孔贵嫔躲胭脂井被俘。\"商女不知亡国恨\"杜诗讽此。",
          regime="chen"),
    ],

    "sui": [
        E("sui_lichun_zhaozhou", "李春设计赵州桥", 605, "sui", "science",
          "隋匠师李春设计修建赵州安济桥,跨度 37 米,大圆拱中嵌四小拱以分洪。世界现存最早最长跨石拱桥,至今已 1400 余年。"),
    ],

    "tang": [
        E("tang_xuanwumen", "玄武门之变", 626, "tang", "war",
          "李世民于玄武门设伏,射杀太子李建成、齐王李元吉。逼父唐高祖李渊立其为太子,旋禅位为唐太宗。中国历史上最有名的宫廷政变。"),
        E("tang_wencheng", "文成公主入藏", 641, "tang", "diplomacy",
          "唐太宗以宗室女文成公主嫁吐蕃赞普松赞干布。携工艺、医药、农耕、文字典籍入藏,促汉藏文化大交流。布达拉宫初建即为迎娶。"),
        E("tang_di_renjie", "狄仁杰 唐室砥柱", 691, "tang", "politics",
          "武则天朝宰相狄仁杰,断疑案、谏废武三思、荐张柬之等贤良,劝武后传位唐子。神龙政变得以归唐李,武后\"以李代武\"狄公功首。"),
        E("tang_li_linfu", "李林甫口蜜腹剑", 740, "tang", "person",
          "唐玄宗后期宰相李林甫,排挤忠良十九年。\"口有蜜,腹有剑\"成奸相典。其用胡将致安禄山掌兵,埋下安史之乱祸根。"),
        E("tang_yang_guifei", "杨贵妃 马嵬坡缢死", 756, "tang", "person",
          "唐玄宗宠杨玉环为贵妃,荔枝快马入长安。安史之乱起,玄宗奔蜀,马嵬坡军士哗变,杨国忠被杀,贵妃缢死佛堂。\"红颜祸水\"千年争议。"),
        E("tang_guo_ziyi", "郭子仪单骑退回纥", 765, "tang", "war",
          "回纥与吐蕃合兵入寇,长安震动。年近七十的郭子仪单骑入回纥营,以旧情说服可汗反与唐联手击吐蕃。\"功盖天下而主不疑\"。"),
        E("tang_bai_juyi", "白居易 诗魔写《长恨歌》", 806, "tang", "culture",
          "白居易,字乐天号香山居士。\"老妪能解\"的平易诗风,作《长恨歌》咏玄宗杨贵妃事,《琵琶行》写琵琶女流落。中唐新乐府运动领袖。"),
        E("tang_yuan_he", "元和中兴 削平藩镇", 815, "tang", "politics",
          "唐宪宗李纯任用裴度、武元衡,十余年间削平淄青李师道、淮西吴元济等强藩。藩镇割据短暂中止,史称元和中兴。"),
        E("tang_niu_li", "牛李党争 四十年党祸", 821, "tang", "politics",
          "宰相牛僧孺、李德裕两派党争四十年,内耗国力。文宗叹\"去河北贼非难,去此朝中朋党难\"。中晚唐衰颓之深因。"),
        E("tang_chu_tang_si_jie", "初唐四杰", 670, "tang", "culture",
          "王勃、杨炯、卢照邻、骆宾王并称初唐四杰。王勃《滕王阁序》\"落霞与孤鹜齐飞\"千古名句。打破六朝绮靡诗风,启盛唐气象。"),
    ],

    "five_dynasties": [
        E("5d_feng_dao", "冯道 五朝宰相", 940, "five_dynasties", "person",
          "冯道历仕后唐、后晋、契丹、后汉、后周五朝十帝皆为相,二十年不倒。世所罕见,自称\"长乐老\"。后世评价两极。"),
        E("5d_qian_liu", "吴越王钱镠 保境安民", 907, "five_dynasties", "politics",
          "钱镠创吴越国,据两浙七十二年。修海塘、筑钱塘江堤、开运河、建灵隐寺。北宋时纳土归宋,吴越免战乱之灾。"),
        E("5d_yelv_abaoji", "耶律阿保机建立辽国", 916, "five_dynasties", "politics",
          "契丹族首领耶律阿保机统一八部,建国号契丹(后改辽),都临潢府。创契丹文字,法度兼收汉法,辽王朝国祚二百余年。"),
    ],

    "song": [
        E("song_beijiu_shi_bingquan", "杯酒释兵权", 961, "song", "politics",
          "宋太祖赵匡胤宴请石守信等高级将领,席间言\"人生如白驹过隙,何不多积金钱、广置田宅享乐\"。诸将翌日皆请辞兵权。和平消除武将威胁。"),
        E("song_kou_zhun", "寇准抗辽 澶渊之盟", 1004, "song", "war",
          "辽萧太后率兵南侵,寇准力排众议劝真宗御驾亲征。宋军于澶州射杀辽将萧挞凛,迫辽议和。\"澶渊之盟\"百年息战。"),
        E("song_yuanhao", "李元昊建立西夏", 1038, "song", "politics",
          "党项族首领李元昊建国号大夏(史称西夏),都兴庆府(今银川)。创西夏文字,与宋、辽鼎立。"),
        E("song_wanyan_aguda", "完颜阿骨打建立金国", 1115, "song", "politics",
          "女真族首领完颜阿骨打统一女真各部,建国号大金,都会宁府。十年后灭辽,十二年后掳徽钦二帝(靖康之变)。"),
        E("song_simaguang", "司马光著《资治通鉴》", 1084, "song", "culture",
          "司马光主编历时十九年完成《资治通鉴》,294 卷,上起战国下迄五代,1362 年编年史。\"鉴于往事,有资于治道\",中国第一部编年体通史。"),
        E("song_shenkuo", "沈括 《梦溪笔谈》", 1086, "song", "science",
          "沈括精通天文、数学、地质、生物、化学,著《梦溪笔谈》26 卷,载毕昇活字印刷、磁针指南、石油等中国古代科技重要记载。"),
        E("song_qingli", "庆历新政 范仲淹改革", 1043, "song", "politics",
          "范仲淹、富弼、欧阳修等推行庆历新政:明黜陟、抑侥幸、精贡举、择官长。十大改革仅一年余被罢。范仲淹\"先天下之忧而忧\"流芳。"),
        E("song_yuefei_jingzhong", "岳母刺字 精忠报国", 1126, "song", "person",
          "岳母姚氏在岳飞背上刺\"精忠报国\"四字,激励其抗金报国。岳家军纪律严明,\"冻死不拆屋,饿死不掳掠\"。被秦桧害死时年仅 39 岁。"),
        E("song_caishi", "采石之战 虞允文败金", 1161, "song", "war",
          "金主完颜亮南侵,文官虞允文临时督师采石矶,以一万八千人破十七万金军。完颜亮被部下所杀,南宋免再陷亡国之灾。"),
        E("song_yan_jiao_zi", "全世界最早纸币 交子", 1023, "song", "economy",
          "北宋成都富商联合发行\"交子\"以代铁钱,后官府接管成为官方纸币。比欧洲早六百余年,世界纸币之祖。"),
    ],

    "yuan": [
        E("yuan_guo_shoujing", "郭守敬编《授时历》", 1281, "yuan", "science",
          "元代天文学家郭守敬制简仪、仰仪等天文仪器,编《授时历》。一年长 365.2425 日,与地球公转周期相差仅 26 秒,比西方格里高利历早 300 年。"),
        E("yuan_zhao_mengfu", "赵孟頫 元代书画双绝", 1310, "yuan", "culture",
          "赵孟頫,宋宗室入元为官。书法\"赵体\"圆润秀丽,绘画提倡复古。其妻管道升、子赵雍亦皆名家,\"管赵之风\"传百年。"),
        E("yuan_dunhuang", "敦煌莫高窟 元代壁画", 1300, "yuan", "religion",
          "敦煌莫高窟历经十六国、北朝、隋唐、五代、宋、西夏、元各代营造。元代壁画与塑像融汉藏佛教风格,千窟巍然,是丝路文明结晶。"),
        E("yuan_huoyaowang", "回回炮 火药西传", 1273, "yuan", "science",
          "蒙古攻襄阳时启用回回工匠造抛石机,称\"回回炮\"。蒙古西征与丝路开通把中国火药、印刷术、指南针经阿拉伯传入欧洲,改变世界。"),
    ],

    "ming": [
        E("ming_qi_jiguang", "戚继光抗倭", 1561, "ming", "war",
          "倭寇侵扰东南沿海,戚继光募义乌矿工组\"戚家军\",创鸳鸯阵。台州九战九捷,基本平定东南倭患。中国军事史上少见百战百胜之将。"),
        E("ming_xu_xiake", "徐霞客游历山川", 1613, "ming", "science",
          "徐霞客二十二岁始旅行,三十四年间踏遍中国十六省。著《徐霞客游记》,精考喀斯特地貌,系统科学考察先驱。\"明季伟人,千古奇人\"。"),
        E("ming_hai_rui", "海瑞 一代清官", 1566, "ming", "politics",
          "海瑞备棺上《治安疏》直谏嘉靖帝。万历时再启用,任应天巡抚抑豪强、行清丈,死后家无余财。\"海青天\"千古清官象征。"),
        E("ming_li_madou", "利玛窦来华传教", 1601, "ming", "religion",
          "意大利传教士利玛窦,着儒服、习汉语,以西方科技为媒介在华传教。绘《坤舆万国全图》、与徐光启合译《几何原本》,中西文化首次大碰撞。"),
        E("ming_yuan_chonghuan", "袁崇焕宁远大捷", 1626, "ming", "war",
          "袁崇焕守宁远,以一万孤军大败努尔哈赤十三万八旗军,炮伤努尔哈赤(数月后亡)。后被崇祯中皇太极反间计凌迟,九边不保。"),
        E("ming_sahuoer", "萨尔浒之战 明军惨败", 1619, "ming", "war",
          "明集兵 11 万分四路攻后金,努尔哈赤\"凭尔几路来,我只一路去\",五日连破三路。明朝在辽东战略主动权丧失,清开国之战。"),
        E("ming_xu_guangqi", "徐光启译《几何原本》", 1607, "ming", "science",
          "徐光启与利玛窦合译欧几里得《几何原本》前六卷,首次系统引入西方数学。又著《农政全书》60 卷,开西学东渐先河。"),
        E("ming_duomen", "夺门之变 英宗复辟", 1457, "ming", "politics",
          "明英宗朱祁镇土木堡被俘归后软禁南宫七年。景泰帝病重,石亨、徐有贞等夜入南宫迎英宗复位,改元天顺。中国历史上罕见太上皇复辟。"),
        E("ming_yu_qian", "于谦保卫北京", 1449, "ming", "war",
          "土木堡之变后瓦剌兵临北京,兵部尚书于谦立朱祁钰为帝(景泰帝),拒迁都南京之议,率军大破瓦剌。后英宗复辟,于谦含冤被杀。\"粉骨碎身全不怕\"。"),
        E("ming_zheng_chenggong", "郑成功收复台湾", 1662, "ming", "war",
          "明遗臣郑成功率两万五千兵围攻荷兰殖民者占据 38 年的台湾,经九个月围攻迫使其投降。台湾重归中国版图,郑成功被尊为民族英雄。"),
    ],

    "qing": [
        E("qing_aobai", "少年康熙智擒鳌拜", 1669, "qing", "politics",
          "顾命大臣鳌拜专权跋扈。十六岁的康熙训练\"布库\"少年游戏团,设计擒拿鳌拜下狱。少年皇帝亲政,清开始走向盛世。"),
        E("qing_san_fan", "康熙平定三藩之乱", 1681, "qing", "war",
          "吴三桂、尚可喜、耿精忠三藩拥兵自重。康熙力排众议下令撤藩,引发三藩叛乱八年。康熙整顿满汉,终擒吴世璠平定。中央集权确立。"),
        E("qing_yake_sa", "雅克萨之战 抗俄保东北", 1685, "qing", "war",
          "沙俄哥萨克侵占黑龙江流域。康熙派萨布素率清军围攻雅克萨城,迫俄议和。1689 年签《尼布楚条约》,确定中俄东段边界,中国近代第一个平等条约。"),
        E("qing_si_ku", "《四库全书》编纂", 1772, "qing", "culture",
          "乾隆下令编《四库全书》,纪昀总纂,十年成 36 万册 36000 卷。中国古代规模最大的丛书。同时也借此查禁\"违碍\"书籍三千余种,文化禁锢与整理并行。"),
        E("qing_he_shen", "和珅倒 嘉庆吃饱", 1799, "qing", "politics",
          "乾隆宠臣和珅二十年专权,贪赃八亿两白银,相当国库十五年收入。乾隆死后嘉庆赐死和珅抄家,白银钜亿。\"和珅跌倒,嘉庆吃饱\"。"),
        E("qing_huoshao_yuanmingyuan", "火烧圆明园", 1860, "qing", "war",
          "第二次鸦片战争英法联军攻入北京,劫掠焚毁圆明园三日。\"万园之园\"百年瑰宝化为灰烬,珍宝散落世界各馆。中华民族永远的伤痛。"),
        E("qing_jiaguwen", "甲骨文发现", 1899, "qing", "culture",
          "国子监祭酒王懿荣染病用药,从龟甲上发现刻字。次年罗振玉、刘鹗等鉴定为商代卜辞。中国信史向上推 800 年,殷墟从此天下闻名。"),
        E("qing_baguo", "八国联军侵华", 1900, "qing", "war",
          "义和团运动爆发,英、美、俄、法、德、日、奥、意八国组联军 5 万入华。慈禧西逃。次年签《辛丑条约》,赔款 4.5 亿两,中国半殖民地化彻底。"),
        E("qing_gongche", "公车上书", 1895, "qing", "politics",
          "甲午战败《马关条约》签订,康有为、梁启超联合在京会试举人 1300 余人上书光绪帝,反对议和,请求变法。维新运动序幕。"),
        E("qing_wuchang", "武昌起义", 1911, "qing", "war",
          "湖北新军中革命党人于武昌发动起义,一夜攻占武汉三镇。各省纷纷响应宣布独立,清朝统治从此瓦解。次年清帝退位,辛亥革命成功。"),
        E("qing_xinyou", "辛酉政变 慈禧垂帘", 1861, "qing", "politics",
          "咸丰帝崩,顾命八大臣与皇后慈安、贵妃慈禧矛盾激化。慈禧联合恭亲王奕䜣发动政变,处死肃顺等三人,慈禧从此垂帘听政四十七年。"),
        E("qing_zhongfa", "中法战争 镇南关大捷", 1885, "qing", "war",
          "法国侵略越南并染指中国西南。冯子材年近七旬率清军于镇南关大破法军,迫法内阁倒台。但清政府\"不败而败\"签订《中法新约\",失越南宗主权。"),
    ],
}


def main():
    summary = {}
    for short, additions in ADDITIONS.items():
        if not additions: continue
        target = EV / f"{short}.json"
        if not target.exists():
            print(f"WARN: {target.name} missing, skipping")
            continue
        with target.open(encoding="utf-8") as f:
            existing = json.load(f)
        existing_ids = {e["id"] for e in existing}
        added = 0
        for ev in additions:
            if ev["id"] in existing_ids:
                print(f"  SKIP {ev['id']} already exists")
                continue
            existing.append(ev)
            added += 1
        with target.open("w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        summary[short] = (added, len(existing))
    print(f"\n{'file':<22} added | total")
    for k, (a, t) in summary.items():
        print(f"  {k:<20} {a:>5} | {t:>5}")
    print(f"  TOTAL added: {sum(a for a,_ in summary.values())}")


if __name__ == "__main__":
    main()
