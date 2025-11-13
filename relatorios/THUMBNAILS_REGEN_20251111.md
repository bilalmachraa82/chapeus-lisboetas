# Regeneração de Thumbnails – 11/11/2025

- Comando: `docker exec chapeus_wordpress wp media regenerate --yes --allow-root`
- Attachments processados: 1 827
- Avisos: IDs antigos inexistentes (`img_01_lifestyle` ID 2034/2031/2023/2040, etc.) – são attachments que já tinham sido removidos e o WP apenas reporta que não encontrou o ficheiro.
- Ficheiros problemáticos (`*-600x822.jpg`) removidos manualmente (5 ocorrências em bone‑22195, bone‑22182, bone‑25025, bone‑25023, bone‑18456g).
