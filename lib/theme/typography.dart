import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Type scale from docs/design-tokens.md.
/// Serif = Noto Serif SC, Sans = Noto Sans SC.
class AppTypography {
  static TextTheme buildTextTheme(Brightness brightness, Color primary) {
    final sansBase = GoogleFonts.notoSansScTextTheme();
    final serif = (double size, FontWeight weight, double lh) =>
        GoogleFonts.notoSerifSc(
          fontSize: size,
          fontWeight: weight,
          height: lh,
          color: primary,
        );
    final sans = (double size, FontWeight weight, double lh) =>
        GoogleFonts.notoSansSc(
          fontSize: size,
          fontWeight: weight,
          height: lh,
          color: primary,
        );

    return sansBase.copyWith(
      displayLarge: serif(28, FontWeight.w700, 1.3),
      displayMedium: serif(22, FontWeight.w600, 1.35),
      headlineMedium: serif(20, FontWeight.w700, 1.4),
      titleLarge: serif(17, FontWeight.w600, 1.4),
      bodyLarge: sans(16, FontWeight.w400, 1.7),
      bodyMedium: sans(14, FontWeight.w400, 1.5),
      bodySmall: sans(12, FontWeight.w400, 1.4),
      labelSmall: sans(11, FontWeight.w400, 1.3),
    ).apply(bodyColor: primary, displayColor: primary);
  }
}
