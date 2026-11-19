"""Studio_1to1_Clone_Kit — 統合クリップ制作エンジン.

両スタジオ（本リポジトリの 1on1 クロンキット + 添付 ZIP のアニメーション・スタジオ）
を統合した、インスタグラム / ユーチューブ向けプロフェッショナル モーション・グラフィックス
制作パイプラインです。

5 スケール（設計図 STUDIO_PORTABLE_BLUEPRINT.md / STUDIO_ARCHITECTURE_AND_TRAINING_GUIDE.md に準拠）:
  1. Warm Analog Vocal Mastering      (24kHz -> 48kHz ステレオ, LADSPA + Pedalboard, -16 LUFS)
  2. Italo-Funk 120 BPM Composer      (FluidSynth GM / シンセサイザー音楽)
  3. Six-SFX Cinema Vault             (ステレオ 48kHz SFX: paper_slide, checklist_tick x6, epic_whoosh, impact, coin, bell_notification)
  4. Whisper Word-Sync Director       (faster-whisper ワード同期, カット/テロップ/アンカー固定)
  5. Morph B-Roll Shader Engine       (frei0r + 265 gl-transitions + 378 LYGIA シェーダー)

サポート機能:
  - ビデオ/オーディオ エフェクト, モーフ, トランジション
  - 3D スケール (Blender headless / CapCut 風プリセット)
  - チャット・ページ制限リマインダー スクリプト
  - インストール/検証スクリプト (install.sh, ensure_engines.sh)
"""

from .cli import main

__all__ = ["main"]
