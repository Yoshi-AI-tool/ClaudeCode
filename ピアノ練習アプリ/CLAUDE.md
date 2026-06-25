# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 現在の開発状況（2026-06）

- **開発中ファイル**：`piano_phase4.html`（`piano_phase3.html` は完成・凍結）
- **Phase 4 実装済み**：右手ボイシング最適化ヒント＋指番号、左手ベースヒント＋指番号
- **次にやること**：右手ボイシングの改善（具体的な指示はその都度ユーザーから出る）
- 詳細は `handover_phase4.md` を参照

## 開発フロー

- **ビルド不要**：`piano_phase4.html` を直接ブラウザで開いて動作確認する
- **動作環境**：Google Chrome のみ（Web MIDI API の制約）
- **フェーズ完成時**：新しいフェーズ番号のファイルとして保存（例：`piano_phase4.html`）
- **編集前に必ずファイル全体を Read で読んでから変更する**（単一ファイルで全コードが連鎖しているため）

## アーキテクチャ概要

単一 HTML ファイルに CSS・HTML・JS をすべて含む構成。外部依存なし。

### ブラウザ API
- **Web MIDI API**：MIDIキーボード入力（`connectMidi` / `setupMidi` / `handleMidi`）
- **Web Audio API**：triangle + sine 倍音合成によるピアノ音（`startNote` / `releaseNote`）
- **localStorage**：コード進行カスタムプリセットの保存

### JS の主要セクション（`// ===` で区切られている）
| セクション | 役割 |
|---|---|
| 定数定義（~L344） | `CHORD_TYPES`, `SCALE_ROOTS`, ダイアトニック配列 |
| 設定UI | モード・キー・コード種チェックボックス切り替え |
| プール構築 | `buildPool` / `rebuildPool` / Fisher-Yates シャッフル |
| 判定 | `checkChord`：ピッチクラス比較、5th省略ロジック |
| タイマー | `startTimer` / `clearTimer`：rAF ループで緑/赤バー描画 |
| 練習フロー（フラッシュカード） | `startPractice` / `nextChord` / `onJudge` |
| タブ切り替え | `switchTab`：flash / prog |
| Phase 3 コード進行（~L674） | プリセット・グリッドエディタ・メトロノーム・結果画面 |
| ピアノ（~L1236） | `buildPiano` / `noteOn` / `noteOff` / ペダル処理 |
| MIDI（~L1329） | `connectMidi` / `handleMidi` |

### タブ・モード構造
- `activeTab`: `'flash'` または `'prog'`
- 鍵盤 (`#shared-piano`) は両モードで共用、練習中のみ表示
- 押鍵チェック (`checkCurrentChord` / `checkProgChord`) は `noteOn` / `noteOff` / `pedalRelease` から呼ばれる

## カラーパレット（変更禁止）

| 用途 | カラーコード |
|---|---|
| 正解・緑 | `#1D9E75` |
| 不正解・赤 | `#E24B4A` |
| アクセント・青 | `#378ADD` |

## コード定義（変更禁止）

```javascript
const CHORD_TYPES = {
  'maj':  { label: '',      required: [0,4,7],    optional: [],   fifth: 7 },
  'm':    { label: 'm',     required: [0,3,7],    optional: [],   fifth: 7 },
  '7':    { label: '7',     required: [0,4,10],   optional: [7],  fifth: 7 },
  'M7':   { label: 'M7',   required: [0,4,11],   optional: [7],  fifth: 7 },
  'm7':   { label: 'm7',   required: [0,3,10],   optional: [7],  fifth: 7 },
  'dim':  { label: 'dim',  required: [0,3,6],    optional: [],   fifth: null },
  'aug':  { label: 'aug',  required: [0,4,8],    optional: [],   fifth: null },
  'sus4': { label: 'sus4', required: [0,5,7],    optional: [],   fifth: null },
  'mM7':  { label: 'mM7',  required: [0,3,11],   optional: [7],  fifth: 7 },
  'dim7': { label: 'dim7', required: [0,3,6,9],  optional: [],   fifth: null },
  'm7b5': { label: 'm7♭5', required: [0,3,6,10], optional: [],   fifth: null },
};
```

- `fifth: null` のコード（dim, aug, sus4, dim7, m7♭5）は5th省略設定の影響を受けない
- `optional` に5thが含まれる7thコードは、5th省略不可のとき `effRequired` に追加される

## 判定ロジックの要点

押鍵ノート → `% 12` → ピッチクラスセット。転回形は常に正解。ペダル保持音（`physPressed` + `activeNodes[m].sustaining`）も判定に含む。

```
必須音が全部揃う？ → NO → タイマーリセット
                   → YES → 余分な音あり？ → YES → 赤タイマー（不正解待ち）
                                          → NO  → 緑タイマー（正解待ち）
```

## Phase 4 実装済み機能

### 右手ボイシングヒント（`applyProgHint` / `computeOptimalVoicing`）
- MIDI 48〜83 の範囲で昇順ボイシングを全列挙し、手幅・半音隣接を除外
- スコアリング：前ボイシングとの音程差最小化 ＋ 7thトップボーナス
- 指番号（青丸）：`data-finger` 属性 → CSS `::after`
- 手の大きさ設定（小12/標準14/大16半音）

### 左手ベースヒント（`computeBassNotes` / `assignBassFinger`）
- 音域 MIDI 36〜55（C2〜G3）、G2 付近を基準
- ハンドポジションモデル：`progBassHandAnchor`（小指位置）から相対オフセットで指決定
  - +7半音以上→指1、+5→指2、+4→指3、+2→指4、0〜1→指5
  - 範囲外はアンカー更新して指5（ポジション移動）
- 指番号（緑丸）：`data-lhand` 属性 → CSS `::after`
- 鍵盤色：水色（`.hint-bass` = `#C8E6FF`）

### Phase 4 ヒント関連の状態変数
```js
let progCurrentVoicing = null;
let progPrevVoicing = null;
let progPrevBassMidi = null;
let progBassHandAnchor = null;
let progHintOn = false;
```

## 次の開発テーマ

**右手ボイシング改善**（具体的な指示はユーザーから都度出る）

参考にすべき理論原則（ユーザーが全て考慮を希望）：
- 左手がベースを弾くので右手でルートを省略するのが基本
- 7th音はトップに配置（コードの「色」を決める最重要音）
- 3rdは必須（長短を決める）、5thは最も省略しやすい
- ボイスリーディング：共通音保持、半音・全音の滑らかな動き
- ドロップ2・ドロップ3ボイシング（ジャズでよく使われる4声）
- 前コードとの音域を近くに保つ転回形の選択

## Phase 5 候補（未着手）

- **バッキング練習**：お手本パターンをアニメーション＋音で表示（正誤判定なし）
  - パターン：ブロックコード、アルペジオ、コンピング等
