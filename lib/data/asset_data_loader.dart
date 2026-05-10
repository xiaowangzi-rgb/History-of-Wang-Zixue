import 'dart:convert';
import 'dart:io';

import 'package:flutter/services.dart' show rootBundle;

import '../models/dynasty.dart';
import '../models/historical_event.dart';
import '../models/person.dart';
import '../models/regime.dart';
import 'hot_update_service.dart';

class LoadedData {
  final List<Dynasty> dynasties;
  final List<Regime> regimes;
  final List<HistoricalEvent> events;
  final List<Person> persons;
  final String schemaVersion;

  LoadedData({
    required this.dynasties,
    required this.regimes,
    required this.events,
    required this.persons,
    required this.schemaVersion,
  });
}

class AssetDataLoader {
  static const _base = 'assets/data';
  final HotUpdateService _hot;

  AssetDataLoader({HotUpdateService? hotUpdate})
      : _hot = hotUpdate ?? HotUpdateService();

  Future<List<dynamic>> _readArray(String filename) async {
    // Prefer remote cache if present, else fall back to bundled asset.
    final cached = await _hot.cachedDataPath(filename);
    final String raw;
    if (cached != null) {
      raw = await File(cached).readAsString();
    } else {
      raw = await rootBundle.loadString('$_base/$filename');
    }
    final decoded = json.decode(raw);
    if (decoded is List) return decoded;
    if (decoded is Map && decoded['records'] is List) {
      return decoded['records'] as List;
    }
    throw FormatException('Unexpected shape in $filename');
  }

  Future<LoadedData> loadAll() async {
    String manifestRaw;
    final cachedManifest = await _hot.cachedDataPath('manifest.json');
    if (cachedManifest != null) {
      manifestRaw = await File(cachedManifest).readAsString();
    } else {
      manifestRaw = await rootBundle.loadString('$_base/manifest.json');
    }
    final manifest = json.decode(manifestRaw) as Map<String, dynamic>;
    final schemaVersion = manifest['_schemaVersion'] as String? ?? 'unknown';

    final dynastiesJson = await _readArray('dynasties.json');
    final regimesJson = await _readArray('regimes.json');
    final eventsJson = await _readArray('events.json');
    final personsJson = await _readArray('persons.json');

    return LoadedData(
      dynasties: dynastiesJson
          .map((e) => Dynasty.fromJson(e as Map<String, dynamic>))
          .toList(),
      regimes: regimesJson
          .map((e) => Regime.fromJson(e as Map<String, dynamic>))
          .toList(),
      events: eventsJson
          .map((e) => HistoricalEvent.fromJson(e as Map<String, dynamic>))
          .toList(),
      persons: personsJson
          .map((e) => Person.fromJson(e as Map<String, dynamic>))
          .toList(),
      schemaVersion: schemaVersion,
    );
  }
}
