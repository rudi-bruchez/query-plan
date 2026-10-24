#!/usr/bin/env bash
# Construit la bibliothèque et publie la visionneuse sur https://sqlplan.pachadata.com
# Usage : visionneuse/deployer.sh   (depuis n'importe où)
set -euo pipefail
cd "$(dirname "$0")/.."
# webpack 4 sous Node 17 et plus exige le fournisseur OpenSSL hérité
NODE_OPTIONS=--openssl-legacy-provider NODE_ENV=production npx webpack >/dev/null
rsync -a --delete --exclude=/qp/ --chmod=D755,F644 \
  visionneuse/index.html visionneuse/plans \
  ryokan:/var/www/sqlplan.pachadata.com/html/
rsync -a --chmod=F644 dist/qp.min.js css/qp.css css/qp_icons.png \
  ryokan:/var/www/sqlplan.pachadata.com/html/qp/
echo "Publié : https://sqlplan.pachadata.com/?p=<nom du plan sans .sqlplan>"
