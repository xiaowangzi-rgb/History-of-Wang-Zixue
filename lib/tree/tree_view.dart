import 'package:flutter/material.dart';

import '../models/dynasty.dart';
import '../models/regime.dart';
import 'layout_engine.dart';
import 'tree_canvas.dart';

/// Scrollable tree view. Calls [onNodeTap] with either a Dynasty or Regime.
class TreeView extends StatefulWidget {
  final List<Dynasty> dynasties;
  final List<Regime> regimes;
  final void Function(Object node) onNodeTap;
  final LayoutConfig config;

  const TreeView({
    super.key,
    required this.dynasties,
    required this.regimes,
    required this.onNodeTap,
    this.config = const LayoutConfig(),
  });

  @override
  State<TreeView> createState() => _TreeViewState();
}

class _TreeViewState extends State<TreeView> {
  late TreeLayout _layout;

  @override
  void initState() {
    super.initState();
    _rebuild();
  }

  @override
  void didUpdateWidget(covariant TreeView old) {
    super.didUpdateWidget(old);
    if (old.dynasties != widget.dynasties ||
        old.regimes != widget.regimes ||
        old.config != widget.config) {
      _rebuild();
    }
  }

  void _rebuild() {
    _layout = TreeLayoutEngine(config: widget.config).layout(
      widget.dynasties,
      widget.regimes,
    );
  }

  @override
  Widget build(BuildContext context) {
    final brightness = Theme.of(context).brightness;
    // Tree dimensions: width = max horizontal span + axis gutter + margin.
    // Compute bound from the layout; node half-width up to 76/2 = 38, plus
    // some breathing room.
    const nodeHalfMax = 50.0;
    final treeWidth = (_layout.width + nodeHalfMax * 2).clamp(280.0, 1600.0);
    final canvasWidth = treeWidth + 56 + 24; // axis + right margin
    final canvasHeight = _layout.height + 32;

    final painter = TreeCanvasPainter(
      layout: _layout,
      brightness: brightness,
      dynastiesForBands: widget.dynasties,
      pxPerYear: widget.config.pxPerYear,
    );

    return InteractiveViewer(
      panEnabled: true,
      scaleEnabled: false,
      constrained: false,
      boundaryMargin: const EdgeInsets.all(80),
      minScale: 1.0,
      maxScale: 1.0,
      child: SizedBox(
        width: canvasWidth,
        height: canvasHeight,
        child: GestureDetector(
          behavior: HitTestBehavior.opaque,
          onTapUp: (details) {
            final node = painter.nodeAt(
              details.localPosition,
              Size(canvasWidth, canvasHeight),
            );
            if (node != null) widget.onNodeTap(node.source as Object);
          },
          child: CustomPaint(
            size: Size(canvasWidth, canvasHeight),
            painter: painter,
          ),
        ),
      ),
    );
  }
}
