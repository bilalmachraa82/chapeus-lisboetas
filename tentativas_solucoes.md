# Registro de Tentativas e Lições

| # | Data | Contexto | Abordagem Testada | Resultado | Porque não resolve completamente | Próximos Passos |
|---|------|----------|-------------------|-----------|---------------------------------|-----------------|
| 1 | 2025-11-11 | Momentos/Home – rostos cortados | Ajuste rápido de CSS (`object-fit: cover` + `object-position` manual para cada card) | ✅ Melhorou enquadramento nas 3 imagens atuais | É manual, não escala para 918 fotos nem garante consistência em uploads futuros | Implementar pipeline automático com detecção de rosto/crop inteligente e especificação de upload |
| 2 | 2025-10-30 | Menu sobreposto pelo hero | Patch de z-index (`.header-wrapper` e `.nav-dropdown` com z-index 10000+) | ✅ Impede que dropdown fique atrás do hero em desktop | Não resolve alinhamento/altura dos submenus quando navegados em sticky header e não documenta hierarquia; comportamento em mobile continua inconsistente | Reavaliar estrutura (#header, `.nav-dropdown-has-arrow`) e definir stack context oficial com testes cross-browser |
