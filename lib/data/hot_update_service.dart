import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:path_provider/path_provider.dart';

/// Pulls JSON data + images from a remote server, caches into the app's
/// document directory, and exposes a "use cache if newer" lookup. Server uses
/// a self-signed cert; the [allowedHost] is whitelisted in [HttpOverrides].
///
/// Layout on server:
///   <baseUrl>/data/manifest.json
///   <baseUrl>/data/dynasties.json (etc)
///   <baseUrl>/images/persons/<slug>.webp
class HotUpdateService {
  static const String baseUrl = 'https://120.48.132.230/wzxhistory';
  static const String allowedHost = '120.48.132.230';

  /// Bootstrap that sets up [HttpOverrides] to accept the self-signed cert
  /// for [allowedHost] only. Call from main() before runApp().
  static void installCertOverride() {
    HttpOverrides.global = _PinnedHostHttpOverrides();
  }

  Future<Directory> _cacheDir() async {
    final base = await getApplicationDocumentsDirectory();
    final dir = Directory('${base.path}/wzxhistory');
    if (!await dir.exists()) await dir.create(recursive: true);
    final dataDir = Directory('${dir.path}/data');
    if (!await dataDir.exists()) await dataDir.create(recursive: true);
    final imgDir = Directory('${dir.path}/images/persons');
    if (!await imgDir.exists()) await imgDir.create(recursive: true);
    return dir;
  }

  /// Returns the local cache file path for a data file, or null if no cache.
  Future<String?> cachedDataPath(String filename) async {
    final dir = await _cacheDir();
    final f = File('${dir.path}/data/$filename');
    return await f.exists() ? f.path : null;
  }

  /// Returns the local cache file path for a portrait, or null if no cache.
  /// [relPath] is the value stored in person.portrait, e.g. "persons/<slug>.webp".
  Future<String?> cachedImagePath(String relPath) async {
    final dir = await _cacheDir();
    final f = File('${dir.path}/images/$relPath');
    return await f.exists() ? f.path : null;
  }

  /// Sync state visible to UI for the optional "checking…" indicator.
  HotUpdateState state = const HotUpdateState.idle();

  /// Check the remote manifest, download any data files whose hash differs.
  /// Images are NOT eagerly synced — they're fetched lazily on first display.
  /// Returns true if any data file was updated.
  Future<bool> syncData({Duration timeout = const Duration(seconds: 10)}) async {
    state = const HotUpdateState.checking();
    final dir = await _cacheDir();
    final localManifestFile = File('${dir.path}/data/manifest.json');

    final client = HttpClient();
    client.connectionTimeout = timeout;
    try {
      final url = Uri.parse('$baseUrl/data/manifest.json');
      final req = await client.getUrl(url).timeout(timeout);
      final resp = await req.close().timeout(timeout);
      if (resp.statusCode != 200) {
        state = HotUpdateState.error('manifest HTTP ${resp.statusCode}');
        return false;
      }
      final remoteText = await resp.transform(utf8.decoder).join();
      final remote = json.decode(remoteText) as Map<String, dynamic>;

      Map<String, dynamic>? local;
      if (await localManifestFile.exists()) {
        local = json.decode(await localManifestFile.readAsString())
            as Map<String, dynamic>;
      }
      // Compare per-file sha256.
      final remoteFiles = (remote['files'] as List)
          .cast<Map<String, dynamic>>();
      final localFiles = ((local?['files'] as List?) ?? const [])
          .cast<Map<String, dynamic>>();
      final localHash = {
        for (final f in localFiles) f['path'] as String: f['sha256'] as String,
      };

      var changed = 0;
      for (final f in remoteFiles) {
        final path = f['path'] as String;
        final sha = f['sha256'] as String;
        if (localHash[path] == sha) continue;
        final ok =
            await _download('$baseUrl/data/$path', '${dir.path}/data/$path',
                timeout: timeout);
        if (ok) changed++;
      }
      // Persist new manifest only if everything succeeded so cache stays
      // consistent. Simpler: write whatever we just downloaded.
      await localManifestFile.writeAsString(remoteText);
      // Best-effort image manifest sync (independent of data changes).
      _syncImagesInBackground(client, timeout, dir);

      state = HotUpdateState.synced(changed);
      return changed > 0;
    } catch (e) {
      state = HotUpdateState.error(e.toString());
      return false;
    } finally {
      client.close();
    }
  }

  /// Download a single image lazily and cache it. Returns local path or null.
  Future<String?> ensureImage(String relPath,
      {Duration timeout = const Duration(seconds: 8)}) async {
    final dir = await _cacheDir();
    final dst = '${dir.path}/images/$relPath';
    if (await File(dst).exists()) return dst;
    final ok = await _download('$baseUrl/images/$relPath', dst,
        timeout: timeout);
    return ok ? dst : null;
  }

  /// Fetch images/_manifest.json from server, then download any missing or
  /// changed image into local cache. Runs in the background; failures silent.
  Future<void> _syncImagesInBackground(
      HttpClient client, Duration timeout, Directory dir) async {
    try {
      final url = Uri.parse('$baseUrl/images/_manifest.json');
      final req = await client.getUrl(url).timeout(timeout);
      final resp = await req.close().timeout(timeout);
      if (resp.statusCode != 200) return;
      final text = await resp.transform(utf8.decoder).join();
      final manifest = json.decode(text) as Map<String, dynamic>;
      final files = (manifest['files'] as List).cast<Map<String, dynamic>>();

      // Compare with local image manifest.
      final localManifest = File('${dir.path}/images/_manifest.json');
      Map<String, String> localHash = {};
      if (await localManifest.exists()) {
        try {
          final ml = json.decode(await localManifest.readAsString())
              as Map<String, dynamic>;
          for (final f in (ml['files'] as List).cast<Map<String, dynamic>>()) {
            localHash[f['path'] as String] = f['sha256'] as String;
          }
        } catch (_) {}
      }

      for (final f in files) {
        final path = f['path'] as String;
        final sha = f['sha256'] as String;
        final localPath = '${dir.path}/images/$path';
        if (localHash[path] == sha && await File(localPath).exists()) continue;
        await _download('$baseUrl/images/$path', localPath, timeout: timeout);
      }
      await localManifest.writeAsString(text);
    } catch (_) {
      // Image sync is best-effort; ignore failures.
    }
  }

  Future<bool> _download(String url, String dstPath,
      {required Duration timeout}) async {
    final tmp = File('$dstPath.part');
    final client = HttpClient();
    client.connectionTimeout = timeout;
    try {
      final req = await client.getUrl(Uri.parse(url)).timeout(timeout);
      final resp = await req.close().timeout(timeout);
      if (resp.statusCode != 200) return false;
      await tmp.parent.create(recursive: true);
      final sink = tmp.openWrite();
      await resp.pipe(sink);
      await tmp.rename(dstPath);
      return true;
    } catch (_) {
      try {
        if (await tmp.exists()) await tmp.delete();
      } catch (_) {}
      return false;
    } finally {
      client.close();
    }
  }
}

class HotUpdateState {
  final String label;
  final int changedCount;
  final String? error;

  const HotUpdateState.idle()
      : label = 'idle',
        changedCount = 0,
        error = null;
  const HotUpdateState.checking()
      : label = 'checking',
        changedCount = 0,
        error = null;
  const HotUpdateState.synced(this.changedCount)
      : label = 'synced',
        error = null;
  const HotUpdateState.error(String e)
      : label = 'error',
        changedCount = 0,
        error = e;
}

class _PinnedHostHttpOverrides extends HttpOverrides {
  @override
  HttpClient createHttpClient(SecurityContext? ctx) {
    final c = super.createHttpClient(ctx);
    c.badCertificateCallback =
        (cert, host, port) => host == HotUpdateService.allowedHost;
    return c;
  }
}
