import 'dart:async';
import 'package:flutter/material.dart';
import 'package:receive_sharing_intent/receive_sharing_intent.dart';

class ShareHandler {
  StreamSubscription<List<SharedMediaFile>>? _sub;

  void init({
    required void Function(String sharedText) onShare,
    required void Function(String sharedText) onInitialShare,
  }) {
    _sub = ReceiveSharingIntent.instance.getMediaStream().listen(
      (List<SharedMediaFile> files) {
        for (final file in files) {
          if (file.path.isNotEmpty) {
            onShare(file.path);
          }
        }
      },
      onError: (err) {
        debugPrint('ShareHandler stream error: $err');
      },
    );

    ReceiveSharingIntent.instance.getInitialMedia().then(
      (List<SharedMediaFile> files) {
        for (final file in files) {
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
