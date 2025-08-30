# 📱✨ Wedding QR Code Generator ✨📱

*A journey into the magical world of image manipulation and pixel wizardry!*

## 🎯 What This Thing Does

Ever wanted to create a QR code that doesn't look like it crawled out of a 2005 flip phone? Well, buckle up buttercup, because this little Python script is about to blow your mind! 

I started this project thinking "how hard could it be to make a pretty QR code?" Turns out, quite hard! But also quite fun. Along the way, I learned about:

- 🎨 **Color theory** (who knew computers could be artists?)
- 🖼️ **Image processing** (pixels are just tiny colored squares, mind = blown)
- 🔍 **QR code internals** (they're basically digital crossword puzzles)
- 🎭 **Alpha blending** (making things see-through is harder than it sounds)

## 🚀 Features That Made Me Go "Wait, I Actually Built This?"

### 🌈 Smart Color Extraction
The script actually *looks* at your logo and goes "hmm, yes, these colors would look fabulous on a QR code." It's like having a tiny digital interior designer living in your computer.

### 🖼️ Logo Integration Without the Ugly
Remember those QR codes with logos that look like someone just slapped a sticker on them? Yeah, we don't do that here. This baby:
- Rounds corners like a pro
- Removes awkward white padding (because nobody likes awkward padding)
- Scales intelligently (no more pixelated nightmares)

### 🌚 Dark Mode Detection
The script is smart enough to detect if your logo is darker than a moonless night and automatically switches to high-contrast black-and-white mode. It's basically artificial intelligence, but for aesthetics.

### 📏 Crispy Pixels
I spent way too much time figuring out why my QR codes looked like they were viewed through frosted glass. Turns out, `LANCZOS` resampling is great for photos but terrible for QR codes. Now we use `NEAREST` interpolation and calculate the perfect box size from the start. The result? Pixels so crisp you could cut yourself on them.

## 🛠️ Installation (The "Oh No, Dependencies" Section)

```bash
pip install qrcode[pil] pillow
```

*Pro tip: If this fails, take a deep breath, count to ten, and make sure you're in the right virtual environment. We've all been there.*

## 🎪 Usage Examples

### The Basic "Make It Pretty" Command
```bash
python main.py \
    --url "https://photos.app.goo.gl/YourAlbumLink" \
    --logo your_amazing_logo.jpg \
    --caption "We Got Married! • Aug 2025" \
    --use-logo-colors \
    --output wedding_magic.png
```

### The "I'm a Control Freak" Command
```bash
python main.py \
    --url "https://photos.app.goo.gl/YourAlbumLink" \
    --logo logo.png \
    --fg "#2c3e50" \
    --bg "#ecf0f1" \
    --caption "Custom Colors Because I Can" \
    --size 2000 \
    --output perfectionist.png
```

### The "Minimalist Aesthetic" Command
```bash
python main.py \
    --url "https://your-link-here.com" \
    --logo simple_logo.png \
    --use-logo-colors \
    --border 0 \
    --output clean_and_minimal.png
```

## 🧠 What I Learned (AKA "Things That Broke My Brain")

### Color Math is Weird
Did you know that green contributes more to perceived brightness than red or blue? Neither did I! The formula `0.299*R + 0.587*G + 0.114*B` is apparently how our eyeballs work. Science is wild.

### QR Codes Are Surprisingly Resilient
You can cover up to 30% of a QR code, and it'll still scan perfectly. That's why we can slap logos right in the middle without breaking anything. Error correction is basically magic.

### PIL/Pillow Has Opinions
- Want smooth scaling? Use `LANCZOS`
- Want crispy pixels? Use `NEAREST`
- Want rounded corners? Draw a mask and pray
- Want transparency? Convert to `RGBA` first or suffer

### File Formats Matter
- PNG: Supports transparency, perfect for logos
- JPEG: No transparency, but smaller files
- PDF: Vector-like scaling, great for printing

## 🎨 The Secret Sauce

The real magic happens in the `select_best_qr_colors()` function. It:

1. Analyze your logo like a digital art critic
2. Calculates contrast ratios (because readability matters)
3. Makes intelligent decisions about which colors will work
4. Falls back gracefully when your logo is just a black square

## 🐛 Things That Might Go Wrong (And How I Fixed Them)

**"My QR code looks like abstract art"**
- Make sure your URL is correct
- Check that your logo file actually exists
- Try reducing the `--logo-scale` if the logo is too big

**"The colors look terrible"**
- Add `--use-logo-colors` for automatic color magic
- Or manually specify `--fg` and `--bg` if you're feeling fancy

**"It won't scan"**
- Keep borders at 4 or higher
- Don't make the logo too big (20% scale is usually perfect)
- Test with multiple QR code scanner apps

## 🎯 Pro Tips From My Journey

1. **Test before printing**: QR codes that look great on screen might not scan well when printed
2. **Size matters**: For business cards, aim for at least 800×800px. For posters, go bigger!
3. **Contrast is king**: Pretty colors mean nothing if people can't scan your code
4. **Logo placement**: The center is usually safe, but test with your specific image

## 🤝 Contributing

Found a bug? Have an idea? Accidentally discovered the meaning of life while debugging? Feel free to contribute! I'm always learning something new about image manipulation.

## 📄 License

Do whatever you want with this code. If it helps you make beautiful QR codes, that's all the payment I need. Maybe send me a photo of your final result – I love seeing this code in the wild!

---

*Built with curiosity, debugged with coffee, and tested with way too many cat photos.* 🐱☕

**P. S.** If you're using this for your wedding, congratulations! May your Wi-Fi be strong, and your QR codes always scan on the first try. 💒📱