import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';

import '../data/app_data_store.dart';
import '../models/dynasty.dart';
import '../models/regime.dart';
import '../sheets/dynasty_detail_sheet.dart';

/// Simple single-line timeline. Each dynasty is a dot on a vertical river,
/// with a label to the right. Parallel regimes are listed inline as text
/// under the parent envelope dynasty (no branches drawn). Designed to feel
/// like a 卷轴 (scroll) rather than a graph.
class SimpleTreeView extends StatelessWidget {
  const SimpleTreeView({super.key});

  @override
  Widget build(BuildContext context) {
    final store = context.read<AppDataController>().store!;
    // Most-recent first (top of screen = today)
    final dynasties = store.dynastiesSortedByYear().reversed.toList();
    final brightness = Theme.of(context).brightness;

    return ListView.builder(
      padding: const EdgeInsets.fromLTRB(0, 8, 16, 32),
      itemCount: dynasties.length,
      itemBuilder: (context, i) {
        final d = dynasties[i];
        final isFirst = i == 0;
        final isLast = i == dynasties.length - 1;
        final regimes = store.regimesByDynasty(d.id);
        return _DynastyRow(
          dynasty: d,
          regimes: regimes,
          brightness: brightness,
          isFirst: isFirst,
          isLast: isLast,
        );
      },
    );
  }
}

class _DynastyRow extends StatelessWidget {
  const _DynastyRow({
    required this.dynasty,
    required this.regimes,
    required this.brightness,
    required this.isFirst,
    required this.isLast,
  });

  final Dynasty dynasty;
  final List<Regime> regimes;
  final Brightness brightness;
  final bool isFirst;
  final bool isLast;

  String _fmtYear(int y) => y < 0 ? '前${-y}' : '$y';

  @override
  Widget build(BuildContext context) {
    final color = dynasty.colorFor(brightness);
    final isLegendary = dynasty.historicity == Historicity.legendary;
    final theme = Theme.of(context);

    return InkWell(
      onTap: () => showDynastyDetail(context, dynasty),
      child: IntrinsicHeight(
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Year gutter
            SizedBox(
              width: 64,
              child: Padding(
                padding: const EdgeInsets.only(top: 18, right: 8),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      _fmtYear(dynasty.endYear),
                      style: GoogleFonts.notoSansSc(
                        fontSize: 11,
                        color: theme.hintColor,
                        fontFeatures: const [FontFeature.tabularFigures()],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            // Center axis with dot
            SizedBox(
              width: 24,
              child: CustomPaint(
                painter: _AxisPainter(
                  color: color,
                  brightness: brightness,
                  isFirst: isFirst,
                  isLast: isLast,
                  isLegendary: isLegendary,
                ),
              ),
            ),
            // Content
            Expanded(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(12, 14, 0, 18),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.baseline,
                      textBaseline: TextBaseline.ideographic,
                      children: [
                        Text(
                          dynasty.name,
                          style: GoogleFonts.notoSerifSc(
                            fontSize: 22,
                            fontWeight: FontWeight.w600,
                            color: isLegendary
                                ? theme.hintColor
                                : color,
                            letterSpacing: 1.5,
                          ),
                        ),
                        const SizedBox(width: 10),
                        Text(
                          '${_fmtYear(dynasty.startYear)} – ${_fmtYear(dynasty.endYear)}',
                          style: GoogleFonts.notoSansSc(
                            fontSize: 11,
                            color: theme.hintColor,
                            fontFeatures: const [
                              FontFeature.tabularFigures()
                            ],
                          ),
                        ),
                      ],
                    ),
                    if (regimes.isNotEmpty) ...[
                      const SizedBox(height: 6),
                      Text(
                        regimes.map((r) => r.name).join('  ·  '),
                        style: GoogleFonts.notoSerifSc(
                          fontSize: 12,
                          color: theme.colorScheme.onSurface
                              .withValues(alpha: 0.65),
                          height: 1.5,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _AxisPainter extends CustomPainter {
  final Color color;
  final Brightness brightness;
  final bool isFirst;
  final bool isLast;
  final bool isLegendary;

  _AxisPainter({
    required this.color,
    required this.brightness,
    required this.isFirst,
    required this.isLast,
    required this.isLegendary,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final cx = size.width / 2;
    final lineColor = brightness == Brightness.dark
        ? Colors.white.withValues(alpha: 0.18)
        : Colors.black.withValues(alpha: 0.15);
    final line = Paint()
      ..color = lineColor
      ..strokeWidth = 1.2;

    // Vertical line
    final topY = isFirst ? size.height * 0.4 : 0.0;
    final bottomY = isLast ? size.height * 0.4 : size.height;
    canvas.drawLine(Offset(cx, topY), Offset(cx, bottomY), line);

    // Dot
    final dotY = size.height * 0.4;
    final dotPaint = Paint()
      ..color = isLegendary ? color.withValues(alpha: 0.4) : color;
    canvas.drawCircle(Offset(cx, dotY), 5, dotPaint);
    // Inner ring for emphasis
    canvas.drawCircle(
      Offset(cx, dotY),
      5,
      Paint()
        ..color = brightness == Brightness.dark
            ? Colors.white.withValues(alpha: 0.15)
            : Colors.black.withValues(alpha: 0.15)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 0.8,
    );
  }

  @override
  bool shouldRepaint(covariant _AxisPainter old) =>
      old.color != color ||
      old.brightness != brightness ||
      old.isFirst != isFirst ||
      old.isLast != isLast;
}
