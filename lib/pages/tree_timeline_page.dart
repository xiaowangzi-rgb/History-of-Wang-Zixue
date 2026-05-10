import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';

import '../data/app_data_store.dart';
import '../models/dynasty.dart';
import '../sheets/dynasty_detail_sheet.dart';
import '../widgets/portrait_image.dart';
import 'simple_tree_view.dart';

enum _ViewMode { list, tree }

class TreeTimelinePage extends StatefulWidget {
  const TreeTimelinePage({super.key});

  @override
  State<TreeTimelinePage> createState() => _TreeTimelinePageState();
}

class _TreeTimelinePageState extends State<TreeTimelinePage> {
  _ViewMode _mode = _ViewMode.list;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        toolbarHeight: 64,
        titleSpacing: 20,
        title: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '王子学历史',
              style: GoogleFonts.notoSerifSc(
                fontSize: 22,
                fontWeight: FontWeight.w700,
                color: theme.colorScheme.onSurface,
                letterSpacing: 2,
              ),
            ),
            const SizedBox(height: 2),
            Text(
              '中国历史长河  ·  尧舜禹至改革开放前',
              style: GoogleFonts.notoSansSc(
                fontSize: 11,
                color: theme.hintColor,
                letterSpacing: 0.5,
              ),
            ),
          ],
        ),
        centerTitle: false,
        actions: [
          IconButton(
            tooltip: _mode == _ViewMode.list ? '时间线视图' : '卡片列表',
            icon: Icon(
              _mode == _ViewMode.list
                  ? Icons.account_tree_outlined
                  : Icons.view_agenda_outlined,
            ),
            onPressed: () => setState(() {
              _mode = _mode == _ViewMode.list
                  ? _ViewMode.tree
                  : _ViewMode.list;
            }),
          ),
          const SizedBox(width: 4),
        ],
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(0.5),
          child: Container(
            height: 0.5,
            color: theme.dividerColor,
          ),
        ),
      ),
      body: SafeArea(
        child: _mode == _ViewMode.list
            ? const _DynastyCardList()
            : const SimpleTreeView(),
      ),
    );
  }
}

class _DynastyCardList extends StatelessWidget {
  const _DynastyCardList();

  @override
  Widget build(BuildContext context) {
    final store = context.read<AppDataController>().store!;
    // Most-recent-first (top of list = today, bottom = legendary times).
    final dynasties = store.dynastiesSortedByYear().reversed.toList();
    final brightness = Theme.of(context).brightness;
    return ListView.builder(
      padding: const EdgeInsets.symmetric(vertical: 8),
      itemCount: dynasties.length,
      itemBuilder: (context, i) =>
          _DynastyCard(dynasty: dynasties[i], brightness: brightness),
    );
  }
}

class _DynastyCard extends StatelessWidget {
  const _DynastyCard({required this.dynasty, required this.brightness});

  final Dynasty dynasty;
  final Brightness brightness;

  String _fmtYear(int y) => y < 0 ? '前${-y}' : '$y';
  String get _yearRange =>
      '${_fmtYear(dynasty.startYear)} – ${_fmtYear(dynasty.endYear)}';
  int get _duration => dynasty.endYear - dynasty.startYear;

  @override
  Widget build(BuildContext context) {
    final color = dynasty.colorFor(brightness);
    final isLegendary = dynasty.historicity == Historicity.legendary;
    final store = context.read<AppDataController>().store!;
    final events = store.eventsByDynasty(dynasty.id);
    final persons = store.personsByDynasty(dynasty.id);
    final regimes = store.regimesByDynasty(dynasty.id);
    final theme = Theme.of(context);
    final scheme = theme.colorScheme;

    final preview = events.take(3).toList();
    String? heroRelPath;
    String? heroLabel;
    for (final p in persons) {
      if (p.portrait != null) {
        heroRelPath = p.portrait;
        heroLabel = p.name;
        break;
      }
    }

    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
      child: Material(
        elevation: 0,
        color: scheme.surface,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: BorderSide(
            color: theme.dividerColor.withValues(alpha: 0.6),
            width: 0.5,
          ),
        ),
        clipBehavior: Clip.antiAlias,
        child: InkWell(
          onTap: () => showDynastyDetail(context, dynasty),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (heroRelPath != null)
                _HeroPortrait(
                  relPath: heroRelPath,
                  label: heroLabel ?? '',
                  color: color,
                )
              else
                Container(
                  height: 4,
                  color: isLegendary
                      ? color.withValues(alpha: 0.4)
                      : color,
                ),
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 18, 20, 18),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Year badge (small, above name)
                    Text(
                      isLegendary
                          ? '$_yearRange  ·  传说'
                          : '$_yearRange  ·  $_duration 年',
                      style: GoogleFonts.notoSansSc(
                        fontSize: 11,
                        color: theme.hintColor,
                        letterSpacing: 1.2,
                        fontFeatures: const [FontFeature.tabularFigures()],
                      ),
                    ),
                    const SizedBox(height: 4),
                    // Dynasty name — big serif in dynasty color
                    Text(
                      dynasty.name,
                      style: GoogleFonts.notoSerifSc(
                        fontSize: 30,
                        fontWeight: FontWeight.w700,
                        color: isLegendary
                            ? theme.hintColor
                            : color,
                        height: 1.1,
                        letterSpacing: 2,
                      ),
                    ),
                    if (dynasty.summary != null &&
                        dynasty.summary!.isNotEmpty) ...[
                      const SizedBox(height: 12),
                      Text(
                        dynasty.summary!,
                        style: GoogleFonts.notoSerifSc(
                          fontSize: 14,
                          height: 1.6,
                          color: scheme.onSurface.withValues(alpha: 0.75),
                        ),
                      ),
                    ],
                    if (preview.isNotEmpty) ...[
                      const SizedBox(height: 14),
                      ...preview.map(
                        (e) => Padding(
                          padding: const EdgeInsets.only(bottom: 6),
                          child: _EventPreviewLine(
                            year: e.year,
                            name: e.name,
                            color: color,
                            theme: theme,
                          ),
                        ),
                      ),
                      if (events.length > preview.length)
                        Padding(
                          padding: const EdgeInsets.only(left: 56),
                          child: Text(
                            '另有 ${events.length - preview.length} 件…',
                            style: GoogleFonts.notoSansSc(
                              fontSize: 11,
                              color: theme.hintColor,
                            ),
                          ),
                        ),
                    ],
                    const SizedBox(height: 16),
                    Container(
                      height: 0.5,
                      color: theme.dividerColor.withValues(alpha: 0.5),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        _MetaPair(
                            label: '事件', value: events.length, theme: theme),
                        const SizedBox(width: 28),
                        _MetaPair(
                            label: '人物',
                            value: persons.length,
                            theme: theme),
                        if (regimes.isNotEmpty) ...[
                          const SizedBox(width: 28),
                          _MetaPair(
                              label: '政权',
                              value: regimes.length,
                              theme: theme),
                        ],
                        const Spacer(),
                        Text(
                          '查看详情',
                          style: GoogleFonts.notoSansSc(
                            fontSize: 12,
                            color: color,
                            letterSpacing: 0.5,
                          ),
                        ),
                        const SizedBox(width: 4),
                        Icon(Icons.arrow_forward,
                            size: 14, color: color),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _EventPreviewLine extends StatelessWidget {
  const _EventPreviewLine({
    required this.year,
    required this.name,
    required this.color,
    required this.theme,
  });
  final int year;
  final String name;
  final Color color;
  final ThemeData theme;

  String _fmtYear(int y) => y < 0 ? '前${-y}' : '$y';

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 56,
          child: Text(
            _fmtYear(year),
            style: GoogleFonts.notoSansSc(
              fontSize: 12,
              color: color.withValues(alpha: 0.85),
              fontWeight: FontWeight.w500,
              fontFeatures: const [FontFeature.tabularFigures()],
            ),
          ),
        ),
        Expanded(
          child: Text(
            name,
            style: GoogleFonts.notoSerifSc(
              fontSize: 14,
              color: theme.colorScheme.onSurface.withValues(alpha: 0.85),
              height: 1.5,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }
}

class _HeroPortrait extends StatelessWidget {
  const _HeroPortrait({
    required this.relPath,
    required this.label,
    required this.color,
  });
  final String relPath;
  final String label;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        ClipRRect(
          borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
          child: AspectRatio(
            aspectRatio: 4 / 3,
            child: PortraitImage(
              relPath: relPath,
              fit: BoxFit.cover,
              alignment: const Alignment(0, -0.2),
              placeholderColor: color.withValues(alpha: 0.15),
              errorBuilder: (_) => Container(color: color),
            ),
          ),
        ),
        // Gradient overlay so the bottom-left label remains readable.
        Positioned.fill(
          child: DecoratedBox(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  Colors.transparent,
                  Colors.black.withValues(alpha: 0.55),
                ],
                stops: const [0.5, 1.0],
              ),
            ),
          ),
        ),
        // Color stripe on top
        Container(
          height: 3,
          color: color,
        ),
        // Person label bottom-left
        Positioned(
          left: 16,
          bottom: 10,
          child: Text(
            label,
            style: GoogleFonts.notoSerifSc(
              color: Colors.white.withValues(alpha: 0.95),
              fontSize: 13,
              fontWeight: FontWeight.w500,
              letterSpacing: 0.5,
            ),
          ),
        ),
      ],
    );
  }
}

class _MetaPair extends StatelessWidget {
  const _MetaPair(
      {required this.label, required this.value, required this.theme});
  final String label;
  final int value;
  final ThemeData theme;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.baseline,
      textBaseline: TextBaseline.ideographic,
      children: [
        Text(
          '$value',
          style: GoogleFonts.notoSerifSc(
            fontSize: 18,
            fontWeight: FontWeight.w600,
            color: theme.colorScheme.onSurface,
          ),
        ),
        const SizedBox(width: 4),
        Text(
          label,
          style: GoogleFonts.notoSansSc(
            fontSize: 11,
            color: theme.hintColor,
          ),
        ),
      ],
    );
  }
}
