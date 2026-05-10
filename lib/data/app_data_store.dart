import 'package:flutter/foundation.dart';

import '../models/dynasty.dart';
import '../models/historical_event.dart';
import '../models/person.dart';
import '../models/regime.dart';
import 'asset_data_loader.dart';
import 'hot_update_service.dart';

/// Read-only in-memory store for the loaded JSON data.
/// Built once at app start; UI consumers read via Provider.
class AppDataStore {
  final List<Dynasty> dynasties;
  final List<Regime> regimes;
  final List<HistoricalEvent> events;
  final List<Person> persons;
  final String schemaVersion;

  late final Map<String, Dynasty> dynastyById;
  late final Map<String, Regime> regimeById;
  late final Map<String, HistoricalEvent> eventById;
  late final Map<String, Person> personById;

  // Inverted indexes for fast queries.
  late final Map<String, List<HistoricalEvent>> _eventsByDynasty;
  late final Map<String, List<Person>> _personsByDynasty;
  late final Map<String, List<Regime>> _regimesByDynasty;

  AppDataStore({
    required this.dynasties,
    required this.regimes,
    required this.events,
    required this.persons,
    required this.schemaVersion,
  }) {
    dynastyById = {for (final d in dynasties) d.id: d};
    regimeById = {for (final r in regimes) r.id: r};
    eventById = {for (final e in events) e.id: e};
    personById = {for (final p in persons) p.id: p};

    _eventsByDynasty = {};
    for (final e in events) {
      _eventsByDynasty.putIfAbsent(e.dynastyId, () => []).add(e);
    }
    for (final list in _eventsByDynasty.values) {
      list.sort((a, b) => a.year.compareTo(b.year));
    }

    _personsByDynasty = {};
    for (final p in persons) {
      _personsByDynasty.putIfAbsent(p.dynastyId, () => []).add(p);
    }
    for (final list in _personsByDynasty.values) {
      list.sort((a, b) {
        final ay = a.birthYear ?? a.reignStart ?? 9999;
        final by = b.birthYear ?? b.reignStart ?? 9999;
        return ay.compareTo(by);
      });
    }

    _regimesByDynasty = {};
    for (final r in regimes) {
      _regimesByDynasty.putIfAbsent(r.parentDynastyId, () => []).add(r);
    }
    for (final list in _regimesByDynasty.values) {
      list.sort((a, b) => a.startYear.compareTo(b.startYear));
    }
  }

  factory AppDataStore.fromLoaded(LoadedData d) => AppDataStore(
        dynasties: d.dynasties,
        regimes: d.regimes,
        events: d.events,
        persons: d.persons,
        schemaVersion: d.schemaVersion,
      );

  List<HistoricalEvent> eventsByDynasty(String dynastyId) =>
      _eventsByDynasty[dynastyId] ?? const [];

  List<Person> personsByDynasty(String dynastyId) =>
      _personsByDynasty[dynastyId] ?? const [];

  List<Regime> regimesByDynasty(String dynastyId) =>
      _regimesByDynasty[dynastyId] ?? const [];

  /// Dynasties sorted by startYear ascending.
  List<Dynasty> dynastiesSortedByYear() =>
      [...dynasties]..sort((a, b) => a.startYear.compareTo(b.startYear));
}

/// Tiny ChangeNotifier wrapper so Provider has a notifier to listen on.
class AppDataController extends ChangeNotifier {
  AppDataController({HotUpdateService? hotUpdate})
      : hotUpdate = hotUpdate ?? HotUpdateService();

  final HotUpdateService hotUpdate;

  AppDataStore? _store;
  Object? _error;

  AppDataStore? get store => _store;
  Object? get error => _error;
  bool get isReady => _store != null;

  void setStore(AppDataStore s) {
    _store = s;
    _error = null;
    notifyListeners();
  }

  void setError(Object e) {
    _error = e;
    notifyListeners();
  }
}
