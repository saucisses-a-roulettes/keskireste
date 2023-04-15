pkgname=keskireste
pkgver=1.0.0
pkgrel=1
pkgdesc="KesKiResTe (what's left?) is a lightweight application to visualize your monthly expenses and incomes balances"
arch=('x86_64')
url="https://github.com/saucisses-a-roulettes/keskireste"
license=('GPL')


package() {
  cd "$srcdir/.."
  install -Dm755 dist/app "$pkgdir/usr/bin/keskireste"
}