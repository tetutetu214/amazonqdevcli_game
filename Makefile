.PHONY: run test clean

# ゲームを実行
run:
	python run.py

# テストを実行
test:
	python -m unittest discover -s tests

# キャッシュファイルを削除
clean:
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*.pyd" -delete
	find . -name ".pytest_cache" -type d -exec rm -rf {} +
	find . -name ".coverage" -delete
	find . -name "htmlcov" -type d -exec rm -rf {} +
