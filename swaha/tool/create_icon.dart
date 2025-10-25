import 'dart:io';
import 'package:image/image.dart';

void main() async {
  // Define colors and sizes
  final backgroundColor = ColorRgb8(0xF0, 0x44, 0x21);
  const imageSize = 1024;
  final logoSize = (imageSize * 0.66).round();

  // Create the background image
  final background = Image(width: imageSize, height: imageSize);
  fill(background, color: backgroundColor);

  // Load the logo
  final logoFile = File('assets/icon/logo_white.png').readAsBytesSync();
  final logo = decodeImage(logoFile)!;

  // Trim the whitespace from the logo
  final trimRect = findTrim(logo);
  final trimmedLogo = copyCrop(logo, x: trimRect[0], y: trimRect[1], width: trimRect[2], height: trimRect[3]);

  // Resize the logo
  final resizedLogo = copyResize(trimmedLogo, width: logoSize, height: logoSize);

  // Calculate the position to center the logo
  final x = (imageSize - resizedLogo.width) ~/ 2;
  final y = (imageSize - resizedLogo.height) ~/ 2;

  // Composite the logo onto the background
  compositeImage(background, resizedLogo, dstX: x, dstY: y);

  // Save the final icon
  await File('assets/icon/icon.png').writeAsBytes(encodePng(background));

  print('Icon created successfully at assets/icon/icon.png');
}
