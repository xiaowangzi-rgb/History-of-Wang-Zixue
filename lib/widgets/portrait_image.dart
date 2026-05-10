import 'dart:io';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../data/app_data_store.dart';

/// Loads a portrait, preferring local cache, falling back to bundled asset,
/// and last-resort fetching from the hot-update server. Caches resolution per
/// path in-memory so subsequent builds don't re-check the filesystem.
///
/// [relPath] is the value stored in person.portrait, e.g.
/// "persons/qing_清圣祖.webp". The bundled location is
/// "data_source/images/<relPath>", the cache location is resolved through
/// HotUpdateService.cachedImagePath.
class PortraitImage extends StatefulWidget {
  const PortraitImage({
    super.key,
    required this.relPath,
    this.fit = BoxFit.cover,
    this.alignment = Alignment.center,
    this.placeholderColor,
    this.errorBuilder,
  });

  final String relPath;
  final BoxFit fit;
  final AlignmentGeometry alignment;
  final Color? placeholderColor;
  final WidgetBuilder? errorBuilder;

  @override
  State<PortraitImage> createState() => _PortraitImageState();
}

// In-memory result cache keyed by relPath. ImageProvider is null when the
// image is not available anywhere.
final Map<String, _Resolved> _resolutionCache = {};

class _Resolved {
  final ImageProvider? provider;
  _Resolved(this.provider);
}

class _PortraitImageState extends State<PortraitImage> {
  late Future<ImageProvider?> _future;

  @override
  void initState() {
    super.initState();
    _future = _resolve();
  }

  @override
  void didUpdateWidget(covariant PortraitImage old) {
    super.didUpdateWidget(old);
    if (old.relPath != widget.relPath) {
      _future = _resolve();
    }
  }

  Future<ImageProvider?> _resolve() async {
    final cached = _resolutionCache[widget.relPath];
    if (cached != null) return cached.provider;

    final hot = context.read<AppDataController>().hotUpdate;
    final assetPath = 'data_source/images/${widget.relPath}';

    // 1. cache file
    final cachedFile = await hot.cachedImagePath(widget.relPath);
    if (cachedFile != null) {
      final p = FileImage(File(cachedFile));
      _resolutionCache[widget.relPath] = _Resolved(p);
      return p;
    }
    // 2. bundled asset
    try {
      final p = AssetImage(assetPath);
      // We can't easily await asset existence without loading; assume it
      // exists. If it doesn't, the Image widget below shows errorBuilder
      // and we'll fall through to a server fetch on a later build.
      _resolutionCache[widget.relPath] = _Resolved(p);
      return p;
    } catch (_) {
      // 3. server fetch
      final localPath = await hot.ensureImage(widget.relPath);
      if (localPath != null) {
        final p = FileImage(File(localPath));
        _resolutionCache[widget.relPath] = _Resolved(p);
        return p;
      }
      _resolutionCache[widget.relPath] = _Resolved(null);
      return null;
    }
  }

  Future<ImageProvider?> _fetchFromServer() async {
    final hot = context.read<AppDataController>().hotUpdate;
    final localPath = await hot.ensureImage(widget.relPath);
    if (localPath != null) {
      final p = FileImage(File(localPath));
      _resolutionCache[widget.relPath] = _Resolved(p);
      return p;
    }
    return null;
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<ImageProvider?>(
      future: _future,
      builder: (context, snap) {
        if (!snap.hasData) {
          return Container(color: widget.placeholderColor ?? Colors.transparent);
        }
        final provider = snap.data;
        if (provider == null) {
          return widget.errorBuilder?.call(context) ??
              Container(color: widget.placeholderColor ?? Colors.transparent);
        }
        return Image(
          image: provider,
          fit: widget.fit,
          alignment: widget.alignment,
          errorBuilder: (ctx, err, stack) {
            // Asset failed — try server one-shot.
            return FutureBuilder<ImageProvider?>(
              future: _fetchFromServer(),
              builder: (c2, snap2) {
                if (!snap2.hasData) {
                  return Container(
                      color: widget.placeholderColor ?? Colors.transparent);
                }
                final p2 = snap2.data;
                if (p2 == null) {
                  return widget.errorBuilder?.call(context) ??
                      Container(
                          color:
                              widget.placeholderColor ?? Colors.transparent);
                }
                return Image(
                  image: p2,
                  fit: widget.fit,
                  alignment: widget.alignment,
                );
              },
            );
          },
        );
      },
    );
  }
}
