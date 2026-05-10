import 'package:flutter/material.dart';

enum Historicity { historical, semiHistorical, legendary }

Historicity _parseHistoricity(String? s) {
  switch (s) {
    case 'legendary':
      return Historicity.legendary;
    case 'semi-historical':
      return Historicity.semiHistorical;
    default:
      return Historicity.historical;
  }
}

Color _parseHex(String hex) {
  final h = hex.replaceAll('#', '');
  return Color(int.parse('FF$h', radix: 16));
}

class Dynasty {
  final String id;
  final String name;
  final int startYear;
  final int endYear;
  final Color color;
  final Color colorDark;
  final Historicity historicity;
  final String? summary;
  final String? heroImage;
  final List<String> regimeIds;
  final String? yearAuthority;

  Dynasty({
    required this.id,
    required this.name,
    required this.startYear,
    required this.endYear,
    required this.color,
    required this.colorDark,
    required this.historicity,
    this.summary,
    this.heroImage,
    this.regimeIds = const [],
    this.yearAuthority,
  });

  factory Dynasty.fromJson(Map<String, dynamic> j) => Dynasty(
        id: j['id'] as String,
        name: j['name'] as String,
        startYear: j['startYear'] as int,
        endYear: j['endYear'] as int,
        color: _parseHex(j['color'] as String),
        colorDark: _parseHex(j['colorDark'] as String),
        historicity: _parseHistoricity(j['historicity'] as String?),
        summary: j['summary'] as String?,
        heroImage: j['heroImage'] as String?,
        regimeIds: (j['regimeIds'] as List?)?.cast<String>() ?? const [],
        yearAuthority: j['_yearAuthority'] as String?,
      );

  Color colorFor(Brightness b) =>
      b == Brightness.dark ? colorDark : color;
}
