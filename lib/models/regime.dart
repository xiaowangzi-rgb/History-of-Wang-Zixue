import 'package:flutter/material.dart';

Color _parseHex(String hex) {
  final h = hex.replaceAll('#', '');
  return Color(int.parse('FF$h', radix: 16));
}

class Regime {
  final String id;
  final String name;
  final int startYear;
  final int endYear;
  final Color color;
  final Color colorDark;
  final String parentDynastyId;
  final String? parentRegimeId;
  final String? mergedIntoRegimeId;
  final List<String> siblingRegimeIds;
  final String? summary;

  Regime({
    required this.id,
    required this.name,
    required this.startYear,
    required this.endYear,
    required this.color,
    required this.colorDark,
    required this.parentDynastyId,
    this.parentRegimeId,
    this.mergedIntoRegimeId,
    this.siblingRegimeIds = const [],
    this.summary,
  });

  factory Regime.fromJson(Map<String, dynamic> j) => Regime(
        id: j['id'] as String,
        name: j['name'] as String,
        startYear: j['startYear'] as int,
        endYear: j['endYear'] as int,
        color: _parseHex(j['color'] as String),
        colorDark: _parseHex(j['colorDark'] as String),
        parentDynastyId: j['parentDynastyId'] as String,
        parentRegimeId: j['parentRegimeId'] as String?,
        mergedIntoRegimeId: j['mergedIntoRegimeId'] as String?,
        siblingRegimeIds:
            (j['siblingRegimeIds'] as List?)?.cast<String>() ?? const [],
        summary: j['summary'] as String?,
      );

  Color colorFor(Brightness b) =>
      b == Brightness.dark ? colorDark : color;
}
