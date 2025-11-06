
import 'package:flutter/material.dart';

class CustomAppBar extends StatelessWidget implements PreferredSizeWidget {
  final List<String> breadcrumbs;
  final VoidCallback onBack;
  final VoidCallback onSettings;
  final Function(int) onBreadcrumbTapped;

  const CustomAppBar({
    super.key,
    required this.breadcrumbs,
    required this.onBack,
    required this.onSettings,
    required this.onBreadcrumbTapped,
  });

  @override
  Widget build(BuildContext context) {
    return AppBar(
      leading: breadcrumbs.length > 1
          ? IconButton(
              icon: const Icon(Icons.arrow_back),
              onPressed: onBack,
            )
          : null,
      title: _buildBreadcrumbs(),
      actions: [
        IconButton(
          icon: const Icon(Icons.settings),
          onPressed: onSettings,
        ),
      ],
    );
  }

  Widget _buildBreadcrumbs() {
    return Row(
      children: breadcrumbs.asMap().entries.map((entry) {
        int idx = entry.key;
        String crumb = entry.value;
        return Row(
          children: [
            InkWell(
              onTap: () => onBreadcrumbTapped(idx),
              child: Text(
                crumb,
                style: const TextStyle(
                  decoration: TextDecoration.underline,
                ),
              ),
            ),
            if (crumb != breadcrumbs.last)
              const Icon(Icons.chevron_right),
          ],
        );
      }).toList(),
    );
  }

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
}
