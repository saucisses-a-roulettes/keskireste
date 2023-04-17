pkgname=keskireste
pkgver=1.0.0
pkgrel=1
pkgdesc="KeskiReste is a lightweight budget management application that allows you to visualize the balance between your expenses and income each month."
arch=('x86_64')
url="https://github.com/saucisses-a-roulettes/keskireste"
license=('GPL')
makedepends=('python-poetry')

build() {
  cd "$srcdir/.."
  poetry install --with=build
  pyinstaller --onefile --windowed --clean src/infrastructure/pyside/app.py
}

package() {
  cd "$srcdir/.."
  install -Dm755 dist/app "$pkgdir/usr/bin/keskireste"
}