
import { test, expect } from '@playwright/test';

test('Word Analysis Card fields populated', async ({ page }) => {
  const base = process.env.E2E_BASE_URL || 'http://localhost:3000';
  const read = process.env.E2E_READ_URL || '/read?book=Genesis&chapter=1&verse=1';
  await page.goto(base + read);

  const toggle = page.getByRole('switch', { name: /Concrete Lens/i });
  await toggle.click();

  await page.getByTestId('token').first().click();
  const panel = page.getByTestId('word-detail-panel');
  await expect(panel).toBeVisible();

  const keys = ['Paleo', 'Transliteration', 'Root', 'Mechanical', 'Final', 'Definitions'];
  for (const k of keys) await expect(panel.getByText(new RegExp(k, 'i'))).toBeVisible();

  await page.getByRole('link', { name: /Why\?/i }).click();
  const modal = page.getByRole('dialog');
  await expect(modal).toBeVisible();
  await expect(modal.getByText(/Alignments/i)).toBeVisible();
  await expect(modal.getByText(/BHSA/i)).toBeVisible();
});
