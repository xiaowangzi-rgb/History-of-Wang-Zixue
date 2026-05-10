import 'package:flutter/material.dart';

import 'colors.dart';
import 'typography.dart';

class AppTheme {
  static ThemeData light() {
    final scheme = ColorScheme.fromSeed(
      seedColor: const Color(0xFF8B6F47), // 青铜 — 中性主色
      brightness: Brightness.light,
      surface: AppColors.bgSurfaceLight,
    ).copyWith(
      surface: AppColors.bgSurfaceLight,
      onSurface: AppColors.textPrimaryLight,
      surfaceContainerHighest: AppColors.bgCardLight,
      outline: AppColors.borderDefaultLight,
    );

    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      colorScheme: scheme,
      scaffoldBackgroundColor: AppColors.bgPrimaryLight,
      textTheme: AppTypography.buildTextTheme(
        Brightness.light,
        AppColors.textPrimaryLight,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: AppColors.bgPrimaryLight,
        foregroundColor: AppColors.textPrimaryLight,
        elevation: 0,
        centerTitle: true,
      ),
      bottomSheetTheme: const BottomSheetThemeData(
        backgroundColor: AppColors.bgBottomSheetLight,
        showDragHandle: true,
      ),
      dividerColor: AppColors.borderDefaultLight,
    );
  }

  static ThemeData dark() {
    final scheme = ColorScheme.fromSeed(
      seedColor: const Color(0xFFA88B5F),
      brightness: Brightness.dark,
      surface: AppColors.bgSurfaceDark,
    ).copyWith(
      surface: AppColors.bgSurfaceDark,
      onSurface: AppColors.textPrimaryDark,
      surfaceContainerHighest: AppColors.bgCardDark,
      outline: AppColors.borderDefaultDark,
    );

    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorScheme: scheme,
      scaffoldBackgroundColor: AppColors.bgPrimaryDark,
      textTheme: AppTypography.buildTextTheme(
        Brightness.dark,
        AppColors.textPrimaryDark,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: AppColors.bgPrimaryDark,
        foregroundColor: AppColors.textPrimaryDark,
        elevation: 0,
        centerTitle: true,
      ),
      bottomSheetTheme: const BottomSheetThemeData(
        backgroundColor: AppColors.bgBottomSheetDark,
        showDragHandle: true,
      ),
      dividerColor: AppColors.borderDefaultDark,
    );
  }
}
