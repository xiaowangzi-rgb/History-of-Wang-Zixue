import '../models/dynasty.dart';
import '../models/regime.dart';

enum NodeKind { dynasty, regime }

/// One laid-out node in tree-canvas coordinates.
/// Y axis: y = -year * pxPerYear. So earlier years have smaller y (more
/// negative), drawn lower on screen when origin is at the bottom.
class TreeNode {
  final String id;
  final NodeKind kind;
  final String name;
  final int startYear;
  final int endYear;
  final double x;
  final double topY;
  final double bottomY;
  final dynamic source; // Dynasty or Regime
  final Historicity historicity;

  TreeNode({
    required this.id,
    required this.kind,
    required this.name,
    required this.startYear,
    required this.endYear,
    required this.x,
    required this.topY,
    required this.bottomY,
    required this.source,
    this.historicity = Historicity.historical,
  });

  double get height => bottomY - topY;
  double get centerY => (topY + bottomY) / 2;
}

class TreeEdge {
  final String fromId;
  final String toId;
  final double x1, y1, x2, y2;

  TreeEdge({
    required this.fromId,
    required this.toId,
    required this.x1,
    required this.y1,
    required this.x2,
    required this.y2,
  });
}

class TreeLayout {
  final List<TreeNode> nodes;
  final List<TreeEdge> edges;
  final double minY;
  final double maxY;
  final double minX;
  final double maxX;

  TreeLayout({
    required this.nodes,
    required this.edges,
    required this.minY,
    required this.maxY,
    required this.minX,
    required this.maxX,
  });

  double get height => maxY - minY;
  double get width => maxX - minX;
}

class LayoutConfig {
  final double pxPerYear;
  final double mainColumnX;
  final double regimeColumnSpacing;

  const LayoutConfig({
    this.pxPerYear = 0.45,
    this.mainColumnX = 0,
    this.regimeColumnSpacing = 80,
  });
}

/// Dynasties that exist purely as time-range envelopes for parallel regimes.
/// We skip drawing a box for them (the regimes carry the visual). The
/// background band is still drawn so the user knows the era's identity.
const _envelopeDynasties = <String>{
  'dynasty_three_kingdoms',
  'dynasty_sixteen_kingdoms',
  'dynasty_southern_northern',
  'dynasty_five_dynasties_ten_kingdoms',
};

class TreeLayoutEngine {
  final LayoutConfig config;
  TreeLayoutEngine({this.config = const LayoutConfig()});

  TreeLayout layout(List<Dynasty> dynasties, List<Regime> regimes) {
    final nodes = <TreeNode>[];
    final edges = <TreeEdge>[];

    final px = config.pxPerYear;
    double y(int year) => -year * px;

    // 1. Main dynasty column. Envelope dynasties are skipped (their regimes
    // carry the visual; we still draw their background band elsewhere).
    final sortedDyn = [...dynasties]
      ..sort((a, b) => a.startYear.compareTo(b.startYear));
    for (final d in sortedDyn) {
      if (_envelopeDynasties.contains(d.id)) continue;
      nodes.add(TreeNode(
        id: d.id,
        kind: NodeKind.dynasty,
        name: d.name,
        startYear: d.startYear,
        endYear: d.endYear,
        x: config.mainColumnX,
        topY: y(d.endYear),
        bottomY: y(d.startYear),
        source: d,
        historicity: d.historicity,
      ));
    }

    // 2. Regimes — split per parent dynasty into left/right columns.
    final byParent = <String, List<Regime>>{};
    for (final r in regimes) {
      byParent.putIfAbsent(r.parentDynastyId, () => []).add(r);
    }

    for (final entry in byParent.entries) {
      final list = [...entry.value]..sort((a, b) {
        // Stable order: by name to keep layout deterministic.
        return a.name.compareTo(b.name);
      });
      final n = list.length;
      // Skip column 0 (reserved for main dynasty). Layout uses fractional
      // columns: for n=3 → [-1.5, -0.5, +0.5, +1.5] then drop the central
      // 0 — actually we just split into left half and right half.
      final leftCount = n ~/ 2;
      final rightCount = n - leftCount;
      for (var i = 0; i < n; i++) {
        final r = list[i];
        late double col;
        if (i < leftCount) {
          // i = 0 → leftmost; closer to center as i grows
          col = -(leftCount - i) - 0.5;
        } else {
          final j = i - leftCount; // 0-based index into right side
          col = j + 0.5;
        }
        final rx = config.mainColumnX + col * config.regimeColumnSpacing;
        nodes.add(TreeNode(
          id: r.id,
          kind: NodeKind.regime,
          name: r.name,
          startYear: r.startYear,
          endYear: r.endYear,
          x: rx,
          topY: y(r.endYear),
          bottomY: y(r.startYear),
          source: r,
        ));
      }
    }

    // 3. Edges from parentRegime / mergedInto.
    final byId = {for (final n in nodes) n.id: n};
    for (final r in regimes) {
      if (r.parentRegimeId != null) {
        final parent = byId[r.parentRegimeId];
        final child = byId[r.id];
        if (parent != null && child != null) {
          edges.add(TreeEdge(
            fromId: parent.id,
            toId: child.id,
            x1: parent.x,
            y1: parent.topY,
            x2: child.x,
            y2: child.bottomY,
          ));
        }
      }
      if (r.mergedIntoRegimeId != null) {
        final into = byId[r.mergedIntoRegimeId];
        final from = byId[r.id];
        if (into != null && from != null) {
          edges.add(TreeEdge(
            fromId: from.id,
            toId: into.id,
            x1: from.x,
            y1: from.topY,
            x2: into.x,
            y2: into.bottomY,
          ));
        }
      }
    }

    // 4. Bounds.
    var minY = double.infinity;
    var maxY = double.negativeInfinity;
    var minX = double.infinity;
    var maxX = double.negativeInfinity;
    for (final n in nodes) {
      if (n.topY < minY) minY = n.topY;
      if (n.bottomY > maxY) maxY = n.bottomY;
      if (n.x < minX) minX = n.x;
      if (n.x > maxX) maxX = n.x;
    }

    return TreeLayout(
      nodes: nodes,
      edges: edges,
      minY: minY,
      maxY: maxY,
      minX: minX,
      maxX: maxX,
    );
  }
}
