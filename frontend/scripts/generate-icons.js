const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const sizes = [16, 32, 64, 128, 192, 512];
const publicDir = path.join(__dirname, '../public');

async function generateIcons() {
  const svgBuffer = fs.readFileSync(path.join(publicDir, 'logo.svg'));

  for (const size of sizes) {
    await sharp(svgBuffer)
      .resize(size, size)
      .png()
      .toFile(path.join(publicDir, `logo${size}.png`));
  }

  // Générer favicon.ico (16x16, 32x32)
  await sharp(svgBuffer).resize(32, 32).toFile(path.join(publicDir, 'favicon.ico'));
}

generateIcons().catch(console.error);
