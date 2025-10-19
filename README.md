# 🎩 Chapéus Lisboetas - Guia Completo

Este projeto contém o desenvolvimento completo de um site de e-commerce para Chapéus Lisboetas, incluindo:

## 📁 Estrutura do Projeto

- **Configuração do WordPress**: Scripts e arquivos para configuração completa do site
- **Catálogo de Produtos**: Scripts para importação e gestão de produtos
- **Processamento de Imagens**: Ferramentas para otimização e tratamento de imagens
- **Automação**: Scripts Python para automação de tarefas
- **Relatórios**: Ferramentas de QA e auditoria

## 🚀 Começando

### Pré-requisitos

- WordPress instalado
- WooCommerce configurado
- Python 3.8+
- Node.js (para algumas ferramentas)

### Instalação

1. Clone este repositório:
```bash
git clone https://github.com/seu-usuario/chapeus-lisboetas.git
cd chapeus-lisboetas
```

2. Configure o ambiente:
```bash
# Copie o arquivo de exemplo de variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

3. Execute o script de configuração:
```bash
./setup-wordpress-complete.sh
```

## 📦 Scripts Principais

- `setup-wordpress-complete.sh`: Configuração completa do WordPress
- `import_to_wordpress.py`: Importação de produtos para o WordPress
- `upload_images_final.php`: Upload de imagens para o WordPress
- `fix_products_display_final.php`: Correção de problemas de exibição

## ��️ Gestão de Imagens

O projeto inclui ferramentas para:
- Classificação automática de imagens
- Otimização de imagens para web
- Geração de thumbnails
- Upload em lote

## 📊 Relatórios

- `visual_qa_report.json`: Relatório de QA visual
- `image_curation_report.json`: Relatório de curadoria de imagens
- `qa_audit_report.json`: Auditoria completa do projeto

## 🤝 Contribuição

1. Fork este repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am "Adiciona nova feature"`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📞 Contato

Seu Nome - [seu-email@exemplo.com](mailto:seu-email@exemplo.com)

## 🙏 Agradecimentos

- Agradecimentos especiais a todos que contribuíram para este projeto.
