"""
japanize-matplotlibのインポート問題をデバッグするためのスクリプト
"""

import sys
import matplotlib

print(f"Python version: {sys.version}")
print(f"Matplotlib version: {matplotlib.__version__}")
print(f"Matplotlib backend: {matplotlib.get_backend()}")
print(f"Matplotlib config directory: {matplotlib.get_configdir()}")
print(f"Matplotlib data path: {matplotlib.get_data_path()}")
print(f"Matplotlib font list: {matplotlib.font_manager.findSystemFonts(fontpaths=None)[:5]}")  # 最初の5つだけ表示

try:
    import japanize_matplotlib
    print("japanize_matplotlib successfully imported")
    
    # 使用されるフォント名を表示
    import matplotlib.pyplot as plt
    
    # 新しいフィギュアとサブプロット
    plt.figure(figsize=(10, 6))
    plt.title("日本語タイトル")
    plt.xlabel("横軸ラベル")
    plt.ylabel("縦軸ラベル")
    
    # IPAフォントが登録されているか確認
    from matplotlib.font_manager import FontManager
    fm = FontManager()
    print("\nAvailable fonts containing 'IPA':")
    ipa_fonts = [f.name for f in fm.ttflist if 'IPA' in f.name]
    print(ipa_fonts)
    
    # 現在のフォント設定を表示
    print("\nCurrent font settings:")
    print(f"Default font family: {plt.rcParams['font.family']}")
    print(f"Default font: {plt.rcParams['font.sans-serif']}")
    
    # 画像をファイルに保存
    plt.savefig('debug_japanize_test.png')
    print("Image saved as debug_japanize_test.png")
    plt.close()
    
except ImportError as e:
    print(f"Error importing japanize_matplotlib: {e}")
    print("\nTrying to find the package:")
    try:
        import pip
        try:
            # pipコマンドで確認
            import subprocess
            result = subprocess.run(["pip", "list"], capture_output=True, text=True)
            print(result.stdout.split('\n')[:20])  # 最初の20行だけ表示
            
            print("\nSearching for japanize-matplotlib in installed packages:")
            result = subprocess.run(["pip", "show", "japanize-matplotlib"], capture_output=True, text=True)
            print(result.stdout)
        except Exception as e:
            print(f"Error running pip commands: {e}")
    except ImportError:
        print("Pip module not available")
except Exception as e:
    print(f"Other error: {e}")