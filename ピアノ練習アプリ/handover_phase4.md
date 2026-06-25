# ピアノ練習アプリ Phase 4 引き継ぎメモ

## 開発環境

- **ブラウザ**：Google Chrome のみ（Web MIDI API の制約）
- **ビルド不要**：`piano_phase4.html` を直接 Chrome で開くだけ
- **外部依存なし**：1ファイル完結

---

## 必要なファイル

| ファイル | 役割 |
|---|---|
| `piano_phase4.html` | **メイン開発ファイル**（これだけあれば動く） |
| `CLAUDE.md` | Claude Code 向け開発ガイド |
| `SPEC.md` | Phase 1〜3 仕様書 |
| `handover_phase4.md` | このファイル |

---

## 実装済み（Phase 1〜3）

### Phase 1
- ピアノ鍵盤 UI（MIDI 21〜108、88鍵フル）
- Web MIDI API 接続・自動検出
- サスティンペダル対応（CC#64）
- Web Audio API による倍音合成ピアノ音（triangle + sine）
- 音量スライダー

### Phase 2：フラッシュカードモード
- 11種コード × 12ルートから出題（設定でフィルタ可）
- 出題方式：完全ランダム / キー指定（ダイアトニック・自由）
- 5th省略設定
- コード判定：ピッチクラス比較、転回形OK、ペダル音込み
- Fisher-Yates シャッフルでデッキ管理（偏りなし）
- ヒント機能（iOS風トグルスイッチ）：ルート=オレンジ、他=黄色
- スコア：正解/不正解/正解率/連続正解

### Phase 3：コード進行モード
- プリセット 14種（カノン、J-POP、ジャズ系4種 etc.）
- グリッドエディタ（小節×拍でコード入力）
- カスタム進行を localStorage に保存
- メトロノームモード：BPM に合わせて自動進行
- 自由モード：正解したら次の拍に進む
- 自動 BPM 調整（全正解で上昇、ミスで低下）
- 練習結果表示（苦手コード一覧、弱点フラッシュカード送り）
- ヒント機能（同上）

### ジャズプリセット（Phase 3 追加分）
- ターンアラウンド（IM7-VI7-IIm7-V7）
- マイナー II-V-I（IIm7♭5-V7-Im7）
- 枯れ葉（8コード）
- ジャズブルース（12コード）

---

## 実装済み（Phase 4）

### 右手ボイシングヒント

**表示タイミング**：ヒントON 時、コード表示と同時に鍵盤をハイライト

**アルゴリズム**：
1. 対象コードの必須音（5th省略設定考慮）のピッチクラスを取得
2. MIDI 48〜83（C3〜B5）の範囲で昇順ボイシングを全列挙（順列）
3. フィルタ：
   - 手の幅（設定値）以内
   - 隣接音が半音差なし（弾けない）
4. スコアリング：
   - 前ボイシングとの音程差の合計 × 2（ボイスリーディング最小化）
   - 7thコードの場合、7度がトップにあると -5 ボーナス
   - スパンが広いほど微小ペナルティ（× 0.2）
5. 最小スコアを採用

**指番号アサイン**（右手）：
- 2音：1, 5
- 3音：スパン≤7半音なら 1,2,5 / それ以外 1,3,5
- 4音：上2音の間隔≥4半音なら 1,2,3,5 / それ以外 1,2,4,5

**手の大きさ設定**（設定パネル内）：
- 小（オクターブ・12半音）
- 標準（9度・14半音）← デフォルト
- 大（10度・16半音）

**CSS 表示**：
- 鍵盤のルート音：オレンジ（`.hint-root`）
- 他のコードトーン：黄色（`.hint`）
- 指番号：青丸（`data-finger` 属性 + `::after` 疑似要素）

### 左手ベースヒント

**音域**：MIDI 36〜55（C2〜G3）、G2（MIDI 43）付近を基準

**指番号アサイン**（左手）：ハンドポジションモデル
- `progBassHandAnchor`（小指の位置）を記録
- 現在音 − アンカー = オフセット で指を決定：
  - ≥ 7 半音 → 指1（親指）
  - ≥ 5 半音 → 指2
  - ≥ 4 半音 → 指3
  - ≥ 2 半音 → 指4
  - 0〜1 半音 → 指5（小指）
  - 範囲外（マイナスまたは 8 半音超）→ 指5でアンカー更新（ポジション移動）
- 例：Cで指5 → Gへ（+7半音）= 指1 ✓

**CSS 表示**：
- 鍵盤：水色（`.hint-bass`）
- 指番号：緑丸（`data-lhand` 属性 + `::after` 疑似要素）

---

## カラーパレット（変更禁止）

| 用途 | コード |
|---|---|
| 正解・緑 | `#1D9E75` |
| 不正解・赤 | `#E24B4A` |
| アクセント・青 | `#378ADD` |
| 右手ヒント：ルート | `#FFD0A0` |
| 右手ヒント：他 | `#FFF3CD` |
| 左手ヒント | `#C8E6FF` |

---

## 主要 JS 変数・関数（Phase 4 追加分）

### 状態変数

```js
let progCurrentVoicing = null;   // 現在の右手ボイシング（MIDIノート配列）
let progPrevVoicing = null;      // 前コードのボイシング（スコアリング用）
let progHintOn = false;
let progPrevBassMidi = null;     // 前コードのベース音
let progBassHandAnchor = null;   // 左手ハンドポジションのアンカー（小指位置）
```

### 関数

| 関数 | 役割 |
|---|---|
| `generateAscendingVoicings(pcs, min, max)` | 昇順ボイシング全列挙 |
| `computeOptimalVoicing(chord)` | 最適右手ボイシング選択 |
| `assignFingers(voicing)` | 右手指番号アサイン |
| `computeBassNotes(chord)` | 左手ベース音選択（MIDI配列を返す） |
| `assignBassFinger(bassMidi)` | 左手指番号アサイン（アンカーモデル） |
| `applyProgHint(chord)` | 右手+左手を鍵盤にハイライト |
| `toggleProgHint()` | ヒントON/OFF切り替え |
| `getMaxHandSpan()` | 設定から手幅（半音数）取得 |

### リセットが必要な箇所

`progBassHandAnchor` と `progPrevBassMidi` は以下でリセット：
- `startProgPractice()`：練習開始時
- `stopProgPractice()`：練習停止時
- `advanceProgBeat()`：次拍に進む際（`progPrevVoicing` の更新と同タイミング）

---

## Phase 4 未実装・課題

### 改善候補

- [ ] 右手ボイシングでルートを省略（左手がベースを弾くため）する実装（理論的には推奨）
- [ ] 左手をルート1音でなくルート+5th（コンピング）に拡張する設定
- [ ] バッキングパターン練習（アルペジオ・ブロックコード・コンピング）
- [ ] 正解後に「推奨転回形」テキスト表示（現在は鍵盤ハイライトのみ）

### 既知の制限

- 右手ボイシング範囲は固定（MIDI 48〜83）。上限・下限の設定化は未実装
- ハンドポジションアンカーは練習開始時のみリセット（ループ継続中は維持）
- ヒントはコード進行モード専用（フラッシュカードは構成音ハイライトのみ・指番号なし）

---

## コード定義（変更禁止）

```js
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
