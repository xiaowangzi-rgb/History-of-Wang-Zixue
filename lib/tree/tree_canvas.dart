import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../models/dynasty.dart';
import '../models/regime.dart';
import 'layout_engine.dart';

/// Editorial / ink-paper style: outline nodes with serif typography. Colour is
/// used as accent (border, name), never solid fill. Connection lines are
/// right-angle git-style with small endpoint dots. Background bands are barely
/// perceptible (alpha 0.04). Year axis has a single hairline rule.
class TreeCanvasPainter extends CustomPainter {
  final TreeLayout layout;
  final Brightness brightness;
  final List<Dynasty> dynastiesForBands;
  final double yearAxisWidth;
  final double pxPerYear;

  TreeCanvasPainter({
    required this.layout,
    required this.brightness,
    required this.dynastiesForBands,
    required this.pxPerYear,
    this.yearAxisWidth = 64,
  });

  bool get _dark => brightness == Brightness.dark;

  Color get _ink => _dark ? Colors.white : const Color(0xFF1A1A1A);
  Color get _inkSoft => _dark ? Colors.white70 : const Color(0xFF5A5751);
  Color get _inkFaint =>
      _dark ? Colors.white30 : const Color(0xFFB0A89D);

  double get _yShift => -layout.minY;

  @override
  void paint(Canvas canvas, Size size) {
    canvas.save();
    canvas.translate(0, _yShift);

    final treeAreaWidth = size.width - yearAxisWidth;
    final treeOffsetX = yearAxisWidth + treeAreaWidth / 2;

    _paintBands(canvas, size);
    _paintAxis(canvas, size);
    // Edges intentionally omitted: in parallel-regime eras (北朝东西魏 /
    // 五代序贯 / 南朝继承) edges crossed sibling nodes and added more visual
    // noise than information. The era's structure is now carried by background
    // bands + spatial proximity alone.
    _paintNodes(canvas, treeOffsetX);

    canvas.restore();
  }

  void _paintBands(Canvas canvas, Size size) {
    for (final d in dynastiesForBands) {
      final color = d.colorFor(brightness);
      final paint = Paint()
        ..color = color.withValues(
          alpha: d.historicity == Historicity.legendary ? 0.03 : 0.07,
        );
      final topY = -d.endYear * pxPerYear;
      final bottomY = -d.startYear * pxPerYear;
      canvas.drawRect(
        Rect.fromLTRB(yearAxisWidth, topY, size.width, bottomY),
        paint,
      );
    }
  }

  void _paintAxis(Canvas canvas, Size size) {
    // Single hairline rule on the right edge of the gutter.
    final hairline = Paint()
      ..color = _inkFaint
      ..strokeWidth = 0.5;
    canvas.drawLine(
      Offset(yearAxisWidth - 0.5, layout.minY),
      Offset(yearAxisWidth - 0.5, layout.maxY),
      hairline,
    );

    // Tick + label every 100 years; bigger label every 500.
    final yPerYear = pxPerYear;
    final minYear = (layout.minY / -yPerYear).ceil();
    final maxYear = (layout.maxY / -yPerYear).floor();
    final start = (maxYear ~/ 100) * 100;
    final end = (minYear ~/ 100) * 100;

    final majorStyle = GoogleFonts.notoSerifSc(
      color: _inkSoft,
      fontSize: 11,
      fontWeight: FontWeight.w500,
    );
    final minorStyle = GoogleFonts.notoSerifSc(
      color: _inkFaint,
      fontSize: 10,
      fontWeight: FontWeight.w400,
    );
    final tick = Paint()
      ..color = _inkFaint
      ..strokeWidth = 0.5;

    for (var year = start; year <= end; year += 100) {
      final y = -year * yPerYear;
      final isMajor = year % 500 == 0;
      canvas.drawLine(
        Offset(yearAxisWidth - (isMajor ? 8 : 4), y),
        Offset(yearAxisWidth - 0.5, y),
        tick,
      );
      final label = year < 0 ? '前${-year}' : '$year';
      final tp = TextPainter(
        text: TextSpan(text: label, style: isMajor ? majorStyle : minorStyle),
        textDirection: TextDirection.ltr,
      )..layout(maxWidth: yearAxisWidth - 12);
      tp.paint(canvas, Offset(8, y - tp.height / 2));
    }
  }

  void _paintEdges(Canvas canvas, double treeOffsetX) {
    final line = Paint()
      ..color = _inkFaint
      ..strokeWidth = 1.2
      ..style = PaintingStyle.stroke;
    final dot = Paint()
      ..color = _inkSoft
      ..style = PaintingStyle.fill;

    for (final e in layout.edges) {
      final p1 = Offset(treeOffsetX + e.x1, e.y1);
      final p2 = Offset(treeOffsetX + e.x2, e.y2);
      // Right-angle git-style: vertical from p1 to mid-y, horizontal across,
      // vertical to p2.
      final midY = (p1.dy + p2.dy) / 2;
      final path = Path()
        ..moveTo(p1.dx, p1.dy)
        ..lineTo(p1.dx, midY)
        ..lineTo(p2.dx, midY)
        ..lineTo(p2.dx, p2.dy);
      canvas.drawPath(path, line);
      // Endpoint dots.
      canvas.drawCircle(p1, 2.0, dot);
      canvas.drawCircle(p2, 2.0, dot);
    }
  }

  void _paintNodes(Canvas canvas, double treeOffsetX) {
    const minHeight = 32.0;
    for (final node in layout.nodes) {
      final isDynasty = node.kind == NodeKind.dynasty;
      final w = isDynasty ? 84.0 : 60.0;
      final accent = isDynasty
          ? (node.source as Dynasty).colorFor(brightness)
          : (node.source as Regime).colorFor(brightness);

      final cx = treeOffsetX + node.x;
      var top = node.topY;
      var bottom = node.bottomY;
      if (bottom - top < minHeight) {
        final mid = (top + bottom) / 2;
        top = mid - minHeight / 2;
        bottom = mid + minHeight / 2;
      }
      final rect = Rect.fromLTRB(cx - w / 2, top, cx + w / 2, bottom);

      final isLegendary = node.historicity == Historicity.legendary;
      final radius = isDynasty ? 4.0 : 3.0;
      final rrect = RRect.fromRectAndRadius(rect, Radius.circular(radius));

      // Soft fill — 5%/8% of accent, makes node distinct from band
      // without being loud.
      canvas.drawRRect(
        rrect,
        Paint()
          ..color = accent.withValues(
            alpha: isLegendary ? 0.05 : (isDynasty ? 0.10 : 0.08),
          ),
      );

      // Outline — 1px accent, slightly stronger for dynasty.
      canvas.drawRRect(
        rrect,
        Paint()
          ..color = accent.withValues(alpha: isLegendary ? 0.4 : 0.85)
          ..style = PaintingStyle.stroke
          ..strokeWidth = isDynasty ? 1.2 : 0.9,
      );

      // Label — serif, in accent colour for dynasty (so colour does work
      // through type), in ink colour for regime (subordinate).
      final nameStyle = GoogleFonts.notoSerifSc(
        color: isLegendary
            ? _inkFaint
            : (isDynasty ? accent : _ink),
        fontSize: isDynasty ? 16 : 12,
        fontWeight: isDynasty ? FontWeight.w600 : FontWeight.w500,
        height: 1.1,
      );
      final tp = TextPainter(
        text: TextSpan(text: node.name, style: nameStyle),
        textDirection: TextDirection.ltr,
        textAlign: TextAlign.center,
      )..layout(maxWidth: w - 6);

      final ty = (rect.top + rect.bottom) / 2 - tp.height / 2;
      tp.paint(canvas, Offset(cx - tp.width / 2, ty));

      // Year mini-label below name when there is room.
      if (rect.height >= 44 && isDynasty) {
        final yearStyle = GoogleFonts.notoSansSc(
          color: _inkSoft.withValues(alpha: 0.7),
          fontSize: 9,
          fontWeight: FontWeight.w400,
          letterSpacing: 0.2,
        );
        final yearLabel = _yearRange(node.startYear, node.endYear);
        final ytp = TextPainter(
          text: TextSpan(text: yearLabel, style: yearStyle),
          textDirection: TextDirection.ltr,
        )..layout(maxWidth: w - 4);
        ytp.paint(canvas, Offset(cx - ytp.width / 2, ty + tp.height + 2));
      }
    }
  }

  /// Hit test in canvas-local coordinates.
  TreeNode? nodeAt(Offset point, Size size) {
    final treeAreaWidth = size.width - yearAxisWidth;
    final treeOffsetX = yearAxisWidth + treeAreaWidth / 2;
    final localY = point.dy - _yShift;
    const minHeight = 32.0;
    for (var i = layout.nodes.length - 1; i >= 0; i--) {
      final n = layout.nodes[i];
      final isDynasty = n.kind == NodeKind.dynasty;
      final w = isDynasty ? 84.0 : 60.0;
      final cx = treeOffsetX + n.x;
      var top = n.topY;
      var bottom = n.bottomY;
      if (bottom - top < minHeight) {
        final mid = (top + bottom) / 2;
        top = mid - minHeight / 2;
        bottom = mid + minHeight / 2;
      }
      if (point.dx >= cx - w / 2 &&
          point.dx <= cx + w / 2 &&
          localY >= top &&
          localY <= bottom) {
        return n;
      }
    }
    return null;
  }

  static String _yearRange(int s, int e) {
    String fmt(int y) => y < 0 ? '前${-y}' : '$y';
    return '${fmt(s)} – ${fmt(e)}';
  }

  @override
  bool shouldRepaint(covariant TreeCanvasPainter old) =>
      old.layout != layout || old.brightness != brightness;
}
