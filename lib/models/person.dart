import 'dynasty.dart' show Historicity;

class Person {
  final String id;
  final String name;
  final int? birthYear;
  final int? deathYear;
  final int? reignStart;
  final int? reignEnd;
  final String dynastyId;
  final String? regimeId;
  final String? role;
  final String? summary;
  final String? body;
  final String? portrait;
  final Historicity historicity;
  final List<String> tags;

  Person({
    required this.id,
    required this.name,
    required this.dynastyId,
    this.birthYear,
    this.deathYear,
    this.reignStart,
    this.reignEnd,
    this.regimeId,
    this.role,
    this.summary,
    this.body,
    this.portrait,
    this.portraitThumb,
    this.historicity = Historicity.historical,
    this.tags = const [],
  });

  final String? portraitThumb;

  /// Asset paths for Flutter to load. Returns null if no portrait.
  String? get portraitAsset =>
      portrait == null ? null : 'data_source/images/$portrait';
  String? get portraitThumbAsset =>
      portraitThumb == null ? null : 'data_source/images/$portraitThumb';

  factory Person.fromJson(Map<String, dynamic> j) => Person(
        id: j['id'] as String,
        name: j['name'] as String,
        birthYear: j['birthYear'] as int?,
        deathYear: j['deathYear'] as int?,
        reignStart: j['reignStart'] as int?,
        reignEnd: j['reignEnd'] as int?,
        dynastyId: j['dynastyId'] as String,
        regimeId: j['regimeId'] as String?,
        role: j['role'] as String?,
        summary: j['summary'] as String?,
        body: j['body'] as String?,
        portrait: j['portrait'] as String?,
        portraitThumb: j['_portraitThumb'] as String?,
        historicity: _h(j['historicity'] as String?),
        tags: (j['tags'] as List?)?.cast<String>() ?? const [],
      );

  static Historicity _h(String? s) {
    switch (s) {
      case 'legendary':
        return Historicity.legendary;
      case 'semi-historical':
        return Historicity.semiHistorical;
      default:
        return Historicity.historical;
    }
  }
}
