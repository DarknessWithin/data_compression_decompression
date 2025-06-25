# 🧬 data compression decompression

**Compression Hub** is a modern file compression and decompression tool powered by both classical and custom algorithms including Gzip, Bzip2, LZMA, Zlib, Huffman Coding, LZ77, and RLE. It comes with an interactive web interface to visualize performance, compare sizes, and download results seamlessly.

---

## 🚀 Features

- 🔄 **Compress and Decompress** any file with a single click.
- 🤖 **Auto Mode**: Automatically selects the best compression method based on effectiveness.
- 🧠 **Smart Algorithms**:
  - Built-in: `gzip`, `bz2`, `lzma`, `zlib`
  - Custom: `Huffman`, `LZ77`, `Run-Length Encoding (RLE)`
- 📊 **Real-time Metrics Visualization**:
  - Compression ratio
  - Time taken
  - File size before/after
- 📥 **Instant Download** of processed files.
- 🌗 **Theme Toggle**: Switch between light and dark modes.
- 🕘 **Recent History Tracking** of operations.

---

## 🗂️ Project Structure
```pgsql
Compressionproj/
│
├── api/
│ └── app.py # Main Flask backend with all algorithms and routes
│
├── templates/
│ └── index.html # Frontend UI (no frameworks used)
│
├── requirements.txt # Python dependencies
├── README.md # You're reading it :)
```


---

## ⚙️ Requirements

Make sure you have **Python 3.7+** installed.

Install dependencies with:

```bash
pip install -r requirements.txt
```
requirements.txt includes:
```nginx
Flask
flask-cors
filetype
```
🧪 Running Locally
Navigate to the project root:
```bash
cd CompressionHub
```
Run the Flask server:
```bash
python api/app.py
```
Open the app in your browser:
```arduino
http://localhost:5000
```
🌐 Live Deployment (Render)
The app is configured for deployment on Render:
```pgsql
📄 Environment Setup
Ensure this structure:
├── api/
│   └── app.py
├── templates/
│   └── index.html
├── requirements.txt
```

Set the Start Command on Render as:
```bash
python api/app.py
```
You don’t need any environment variables unless setting custom ports.
🧠 Algorithm Descriptions
| Algorithm                     | Type     | Description                                                 |
| ----------------------------- | -------- | ----------------------------------------------------------- |
| **Gzip, Bz2, LZMA, Zlib**     | Built-in | Standard lossless compression libraries                     |
| **Huffman Coding**            | Custom   | Encodes bytes using a binary prefix tree based on frequency |
| **LZ77**                      | Custom   | Replaces repeated sequences with backward references        |
| **RLE (Run-Length Encoding)** | Custom   | Compresses repeated bytes using counts                      |

Auto mode selects the first method that achieves better-than-original compression.
🖼️ Screenshots
📌 (You can include screenshots of the UI, charts, and file download feature here.)

#🛠️ To Do / Future Improvements
⏱️ Add real-time compression progress bar

🗃️ Support zipped multi-file archives

🔐 Add password-protected file output

📊 Show algorithm-wise performance benchmarks

🙌 Acknowledgements
Flask and Flask-CORS

Chart.js for visualizations

Community resources on compression algorithms

🌍 Multilingual interface


