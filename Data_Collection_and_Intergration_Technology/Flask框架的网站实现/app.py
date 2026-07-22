from flask import Flask, render_template

app = Flask(__name__)

def read_books():
    books = []
    try:
        # 确保 'book.txt' 文件与 app.py 在同一目录下
        with open('book.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # 跳过表头
            for line in lines[1:]:
                parts = line.strip().split()
                if len(parts) >= 3:
                    # 第一个元素是序号，最后一个是分类，中间的是书名
                    book_info = {
                        'id': parts[0],
                        'title': ' '.join(parts[1:-1]),
                        'category': parts[-1]
                    }
                    books.append(book_info)
    except FileNotFoundError:
        print("错误： 'book.txt' 文件未找到。")
    return books

@app.route('/')
def index():
    book_data = read_books()
    return render_template('index.html', books=book_data)

if __name__ == '__main__':
    app.run(debug=True)