"""
第一原理電子状態計算 (DFT / Quantum ESPRESSO) のパラメータ設定ファイル
【ユーザー編集対象 (必要な場合のみ)】
通常はデフォルト設定のままで高精度かつ安定に収束します。
カットオフエネルギーの収束性テストや k点メッシュの変更を行う場合はここを編集します。
"""

DFT_CONFIG = {
    # 波動関数カットオフエネルギー (Ry)
    # 推奨値: 40.0 Ry (PAW擬ポテンシャル下で結合エネルギーが十分収束)
    'ecutwfc': 40.0,

    # 電荷密度カットオフエネルギー (Ry)
    # 推奨値: 320.0 Ry (PAWでは通常 ecutwfc の 8〜10倍を設定)
    'ecutrho': 320.0,

    # SCF電子状態収束閾値 (Ry)
    # 推奨値: 1.0e-5 (力・エネルギーの精度として十分)
    'conv_thr': 1.0e-5,

    # k点サンプリング
    # None: Γ点のみ (K_POINTS gamma)
    # スーパーセル (3x3以上, 9Å以上) では逆格子空間が狭いため None (Γ点) で十分収束します。
    # 単位胞や小さめのセルの場合は (2, 2, 1) などのタプルを指定可能
    'kpts': None,

    # 電子占有・スメアリング設定
    'occupations': 'smearing',
    'smearing': 'gaussian',
    'degauss': 0.01,  # Ry

    # 電子密度ミキシング設定 (SCF収束の安定化)
    'mixing_beta': 0.3,
    'mixing_mode': 'local-TF',  # 表面スラブ特有の電荷振動を抑える局所Thomas-Fermi法
    'electron_maxstep': 200,

    # 擬ポテンシャルファイル名
    'pseudopotentials': {
        'Si': 'Si.upf',
        'C': 'C.upf'
    }
}
