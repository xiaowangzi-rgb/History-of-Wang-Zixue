import 'dynasty.dart' show Historicity;

class HistoricalEvent {
  final String id;
  final String name;
  final int year;
  final int? month;
  final int? day;
  final String dynastyId;
  final String? regimeId;
  final String? category;
  final String summary;
  final String? body;
  final List<String> participants;
  final String? locationName;
  final Historicity historicity;
  final List<String> tags;

  HistoricalEvent({
    required this.id,
    required this.name,
    required this.year,
    this.month,
    this.day,
    required this.dynastyId,
    this.regimeId,
    this.category,
    required this.summary,
    this.body,
    this.participants = const [],
    this.locationName,
    this.historicity = Historicity.historical,
    this.tags = const [],
  });

  factory HistoricalEvent.fromJson(Map<String, dynamic> j) => HistoricalEvent(
        id: j['id'] as String,
        name: j['name'] as String,
        year: j['year'] as int,
        month: j['month'] as int?,
        day: j['day'] as int?,
        dynastyId: j['dynastyId'] as String,
        regimeId: j['regimeId'] as String?,
        category: j['category'] as String?,
        summary: j['summary'] as String,
        body: j['body'] as String?,
        participants:
            (j['participants'] as List?)?.cast<String>() ?? const [],
        locationName: j['locationName'] as String?,
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
