from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os, base64, time, json

app = Flask(__name__, template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates')))
CORS(app)
import gzip, bz2, lzma, zlib, base64, heapq
from collections import Counter

# Built-in Compressors
class BuiltInCompressor:
    def __init__(self, algorithm):
        self.algorithm = algorithm

    def compress(self, data):
        return self._get_func(True)(data)

    def decompress(self, data, _=None):
        return self._get_func(False)(data)

    def _get_func(self, is_compress):
        return {
            'gzip': (gzip.compress, gzip.decompress),
            'bz2': (bz2.compress, bz2.decompress),
            'lzma': (lzma.compress, lzma.decompress),
            'zlib': (zlib.compress, zlib.decompress)
        }[self.algorithm][0 if is_compress else 1]


# Huffman Compression
class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = self.right = None

    def __lt__(self, other): return self.freq < other.freq

class HuffmanCompressor:
    def __init__(self):
        self.codes, self.reverse = {}, {}

    def compress(self, data):
        freq = Counter(data)
        heap = [HuffmanNode(c, f) for c, f in freq.items()]
        heapq.heapify(heap)

        if len(heap) == 1: return bytes([next(iter(freq))]), {'freq': freq, 'padding': 0, 'length': len(data)}

        while len(heap) > 1:
            l, r = heapq.heappop(heap), heapq.heappop(heap)
            parent = HuffmanNode(None, l.freq + r.freq)
            parent.left, parent.right = l, r
            heapq.heappush(heap, parent)

        root = heap[0]
        self._generate_codes(root)

        bitstring = ''.join(self.codes[byte] for byte in data)
        padding = 8 - len(bitstring) % 8
        bitstring += '0' * padding
        compressed = bytearray(int(bitstring[i:i+8], 2) for i in range(0, len(bitstring), 8))

        return bytes(compressed), {'freq': freq, 'padding': padding, 'length': len(data)}

    def _generate_codes(self, node, code=''):
        if node.char is not None:
            self.codes[node.char] = code or "0"
        else:
            self._generate_codes(node.left, code + '0')
            self._generate_codes(node.right, code + '1')

    def decompress(self, data, meta):
        root = self._rebuild_tree(meta['freq'])
        bitstring = ''.join(format(b, '08b') for b in data)[:-meta['padding']]
        output, node = bytearray(), root

        for bit in bitstring:
            node = node.left if bit == '0' else node.right
            if node.char is not None:
                output.append(node.char)
                node = root

        return bytes(output)

    def _rebuild_tree(self, freq):
        heap = [HuffmanNode(c, f) for c, f in freq.items()]
        heapq.heapify(heap)
        while len(heap) > 1:
            l, r = heapq.heappop(heap), heapq.heappop(heap)
            parent = HuffmanNode(None, l.freq + r.freq)
            parent.left, parent.right = l, r
            heapq.heappush(heap, parent)
        return heap[0]


# LZ77
class LZ77Compressor:
    def __init__(self, window=1024): self.window = window

    def compress(self, data):
        i, result = 0, bytearray()
        while i < len(data):
            match_len, match_dist = 0, 0
            for j in range(max(0, i - self.window), i):
                length = 0
                while i + length < len(data) and data[j + length] == data[i + length]:
                    length += 1
                    if j + length >= i: break
                if length > match_len:
                    match_len = length
                    match_dist = i - j
            if match_len > 2:
                next_byte = data[i + match_len] if i + match_len < len(data) else 0
                result.extend([match_dist >> 8, match_dist & 255, match_len, next_byte])
                i += match_len + 1
            else:
                result.extend([0, 0, 0, data[i]])
                i += 1
        return bytes(result), {'length': len(data)}

    def decompress(self, data, _):
        output, i = bytearray(), 0
        while i + 3 < len(data):
            offset = (data[i] << 8) + data[i + 1]
            length = data[i + 2]
            char = data[i + 3]
            for _ in range(length):
                output.append(output[-offset])
            if char != 0 or (offset == 0 and length == 0):
                output.append(char)
            i += 4
        return bytes(output)


# RLE
class RLECompressor:
    def compress(self, data):
        i, out = 0, bytearray()
        while i < len(data):
            count = 1
            while i + count < len(data) and data[i + count] == data[i] and count < 255:
                count += 1
            if count >= 4:
                out.extend([255, count, data[i]])
            else:
                for _ in range(count):
                    if data[i] == 255:
                        out.extend([255, 1, 255])
                    else:
                        out.append(data[i])
            i += count
        return bytes(out), {'length': len(data)}

    def decompress(self, data, _):
        i, out = 0, bytearray()
        while i < len(data):
            if data[i] == 255 and i + 2 < len(data):
                out.extend([data[i + 2]] * data[i + 1])
                i += 3
            else:
                out.append(data[i])
                i += 1
        return bytes(out)


# Compressor Factory
class CompressorFactory:
    compressors = {
        'gzip': lambda: BuiltInCompressor('gzip'),
        'bz2': lambda: BuiltInCompressor('bz2'),
        'lzma': lambda: BuiltInCompressor('lzma'),
        'zlib': lambda: BuiltInCompressor('zlib'),
        'huffman': HuffmanCompressor,
        'lz77': LZ77Compressor,
        'rle': RLECompressor
    }

    @staticmethod
    def get(name):
        if name not in CompressorFactory.compressors:
            raise ValueError(f"Unknown algorithm: {name}")
        return CompressorFactory.compressors[name]()

    @staticmethod
    def get_all():
        return list(CompressorFactory.compressors.keys())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def handle_file():
    uploaded_file = request.files.get('file')
    if not uploaded_file or uploaded_file.filename == '':
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400

    try:
        raw_data = uploaded_file.read()
        operation = request.form.get('operation')
        algorithm = request.form.get('algorithm', 'auto').lower()
        filename = uploaded_file.filename
        original_size = len(raw_data)

        if operation == 'compress':
            chosen_algorithms = [algorithm] if algorithm != 'auto' else CompressorFactory.get_all()
            for algo in chosen_algorithms:
                try:
                    compressor = CompressorFactory.get(algo)
                    start = time.time()
                    result = compressor.compress(raw_data)
                    compressed_data, metadata = result if isinstance(result, tuple) else (result, {})
                    duration = round(time.time() - start, 3)

                    if len(compressed_data) >= original_size:
                        continue

                    response_payload = {
                        'compressed_data': base64.b64encode(compressed_data).decode(),
                        'metadata': metadata,
                        'algorithm': algo,
                        'original_filename': filename
                    }

                    return jsonify({
                        'success': True,
                        'operation': 'compress',
                        'algorithm': algo,
                        'original_size': original_size,
                        'processed_size': len(compressed_data),
                        'compression_ratio': round((original_size - len(compressed_data)) / original_size * 100, 2),
                        'processing_time': duration,
                        'filename': f"{os.path.splitext(filename)[0]}_{algo}.compressed",
                        'file_data': list(json.dumps(response_payload).encode())
                    })

                except Exception:
                    continue

            return jsonify({'success': False, 'error': 'No compression succeeded'}), 400

        elif operation == 'decompress':
            parsed_payload = json.loads(raw_data.decode())
            compressed = base64.b64decode(parsed_payload['compressed_data'])
            meta = parsed_payload.get('metadata', {})
            algo = parsed_payload['algorithm']
            filename = parsed_payload['original_filename']
            decompressor = CompressorFactory.get(algo)
            start = time.time()
            output_data = decompressor.decompress(compressed, meta)
            duration = round(time.time() - start, 3)

            return jsonify({
                'success': True,
                'operation': 'decompress',
                'algorithm': algo,
                'original_size': len(compressed),
                'processed_size': len(output_data),
                'processing_time': duration,
                'filename': filename,
                'file_data': list(output_data)
            })

        return jsonify({'success': False, 'error': 'Unknown operation'}), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'ok',
        'supported_algorithms': CompressorFactory.get_all(),
        'version': '5.0-refactored'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
