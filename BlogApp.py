from flask import Flask, jsonify, request
from BlogItem import db, BlogItem
from functools import reduce

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

# Alte funktion: format_content = lambda content: content if len(content) <= 100 else content[:100] + "..."
create_preview = lambda title, content: f"{title}: {' '.join(content.split()[:5])}..."

@app.route('/blog', methods=['GET'])
def get_all_items():
    sort_by = request.args.get('sort_by', 'default')
    filter_by_length = request.args.get('min_length', 0)
    items = BlogItem.query.all()
    filtered_items = filter(lambda item: len(item.content) >= int(filter_by_length), items)
    transformed_items = map(lambda item: {'item_id': item.item_id, 'title': item.title,
                                          'preview': create_preview(item.title, item.content)}, filtered_items)
    if sort_by == 'length':
        sorted_items = sorted(transformed_items, key=lambda item: len(item['preview']), reverse=True)
    else:
        sorted_items = list(transformed_items)
    total_length = reduce(lambda acc, item: acc + len(item['preview']), sorted_items, 0)
    return jsonify({
        'items': sorted_items,
        'total_length_of_previews': total_length
    })

@app.route('/blog/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = BlogItem.query.get(item_id)
    if item:
        preview_content = create_preview(item.title, item.content)
        return jsonify({'item_id': item.item_id, 'title': item.title, 'content': preview_content})
    return jsonify({'message': 'Item not found'}), 404

@app.route('/blog', methods=['POST'])
def add_item():
    data = request.json
    blog_item = BlogItem(title=data['title'], content=data['content'])
    db.session.add(blog_item)
    db.session.commit()
    return jsonify({'message': 'Item added successfully'}), 201


@app.route('/blog/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.json
    blog_item = BlogItem.query.get(item_id)
    if blog_item:
        blog_item.title = data.get('title', blog_item.title)
        blog_item.content = data.get('content', blog_item.content)
        db.session.commit()
        return jsonify({'message': 'Item updated successfully'}), 200
    return jsonify({'message': 'Item not found'}), 404


@app.route('/blog/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    blog_item = BlogItem.query.get(item_id)
    if blog_item:
        db.session.delete(blog_item)
        db.session.commit()
        return jsonify({'message': 'Item deleted successfully'}), 200
    return jsonify({'message': 'Item not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)