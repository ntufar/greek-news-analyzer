import 'dart:async';
import 'package:flutter/material.dart';
import 'package:receive_sharing_intent/receive_sharing_intent.dart';

class ShareHandler {
  StreamSubscription<List<SharedMediaFile>>? _sub;

  void init({
    required void Function(String sharedText) onShare,
    required void Function(String sharedText) onInitialShare,
  }) {
    // Handle shared content (text, URLs, files)
    _sub = ReceiveSharingIntent.instance.getMediaStream().listen(
      (List<SharedMediaFile> value) {
        debugPrint('ShareHandler: received ${value.length} items');
        for (final file in value) {
          debugPrint('ShareHandler: type=${file.type.value}, path=${file.path}');
          if (file.path.isNotEmpty) {
            onShare(file.path);
          }
        }
      },
      onError: (err) {
        debugPrint('ShareHandler stream error: $err');
      },
    );

    // Handle initial share (when app is launched via share)
    ReceiveSharingIntent.instance.getInitialMedia().then(
      (List<SharedMediaFile> value) {
        debugPrint('ShareHandler: initial share ${value.length} items');
        for (final file in value) {
          debugPrint('ShareHandler: initial type=${file.type.value}, path=${file.path}');
          if (file.path.isNotEmpty) {
            onInitialShare(file.path);
          }
        }
      },
    );
  }

  void dispose() {
    _sub?.cancel();
    ReceiveSharingIntent.instance.reset();
  }
}
