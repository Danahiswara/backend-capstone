"""
app/api/mock_predict.py

Mock Predict Endpoint — TIDAK melakukan inference AI sama sekali.
Tujuan: pembanding uji beban (JMeter) untuk membuktikan bottleneck ada di
AI service (Cloud Run + ONNX inference), bukan di layer FastAPI/database.

Struktur request & response endpoint ini didesain IDENTIK dengan endpoint
/predict asli (lihat app/api/detection.py) agar hasil JMeter bisa
dibandingkan apple-to-apple: base URL saja yang beda, test plan sama persis.
"""

import time
import asyncio
from typing import Optional

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/mock-predict", tags=["Mock Predict (Testing)"])


# ─── Sample hasil deteksi asli (dipakai apa adanya, tidak dihitung ulang) ─────
# Diambil dari hasil real /predict — 3 pola dasar, diduplikasi jadi 23 deteksi
# agar payload size mendekati response asli untuk perbandingan yang adil.
_SAMPLE_BASE = [
    {
        "id": 1, "class": "kapsul", "class_id": 1, "confidence": 1.0,
        "bbox": {"x1": 202.99, "y1": 107.69, "x2": 314.88, "y2": 177.57,
                  "width": 111.89, "height": 69.88},
        "centroid": {"x": 256.83, "y": 142.14},
        "mask_area_px": 4594,
        "polygon": [[202, 116], [202, 136], [206, 141], [216, 147], [264, 169],
                    [297, 177], [311, 151], [302, 138], [264, 123], [228, 108], [207, 111]],
    },
    {
        "id": 2, "class": "kapsul", "class_id": 1, "confidence": 0.9999,
        "bbox": {"x1": 509.89, "y1": 346.04, "x2": 578.03, "y2": 458.06,
                  "width": 68.14, "height": 112.02},
        "centroid": {"x": 542.54, "y": 401.11},
        "mask_area_px": 4573,
        "polygon": [[521, 347], [510, 357], [521, 403], [541, 450], [562, 458],
                    [576, 442], [560, 389], [535, 346], [524, 346]],
    },
    {
        "id": 3, "class": "kapsul", "class_id": 1, "confidence": 0.9999,
        "bbox": {"x1": 43.25, "y1": 175.38, "x2": 157.33, "y2": 269.98,
                  "width": 114.08, "height": 94.6},
        "centroid": {"x": 99.57, "y": 222.03},
        "mask_area_px": 5681,
        "polygon": [[43, 187], [47, 211], [91, 245], [139, 270], [156, 253],
                    [141, 224], [91, 186], [69, 175], [52, 178]],
    },
]


def _build_full_sample(n: int = 23) -> list:
    full = []
    for i in range(n):
        item = dict(_SAMPLE_BASE[i % len(_SAMPLE_BASE)])
        item["id"] = i + 1
        full.append(item)
    return full


_FULL_SAMPLE_DETECTIONS = _build_full_sample(23)

_MOCK_RESPONSE_TEMPLATE = {
    "counts": {"kapsul": 23, "softgel": 0, "tablet": 0, "total": 23},
    "detections": _FULL_SAMPLE_DETECTIONS,
    "image_size": {"width": 640, "height": 640},
    "total_detections": 23,
    "tta_used": True,
}


# ======================
# HEALTH (khusus mock — selalu instant, tidak ada model)
# ======================
@router.get("/health")
def mock_health():
    return {
        "status": "ok",
        "model_status": "ready",
        "model_loaded": True,
        "note": "Ini mock endpoint — tidak ada model AI sungguhan",
    }


# ======================
# PREDICT (MOCK)
# ======================
@router.post("/predict")
async def mock_predict(
    file: UploadFile = File(...),
    use_tta: bool = True,
    artificial_delay_ms: Optional[int] = 0,
):
    """
    Struktur request & response IDENTIK dengan endpoint /predict asli
    (app/api/detection.py) — dipakai sebagai kontrol eksperimen JMeter.

    Parameter tambahan (khusus mock, tidak ada di endpoint asli):
    - artificial_delay_ms: delay buatan (ms) untuk simulasi skenario
      tambahan tanpa AI, misal membuktikan overhead I/O murni backend.

    Default (artificial_delay_ms=0): merespons secepat mungkin — hanya
    overhead baca file + serialize JSON, tanpa inference AI sama sekali.
    """
    t_start = time.perf_counter()

    # Tetap baca file penuh agar overhead I/O upload ikut terukur,
    # sama seperti endpoint asli — supaya perbandingan tetap adil.
    contents = await file.read()
    file_size_kb = len(contents) / 1024

    if artificial_delay_ms and artificial_delay_ms > 0:
        await asyncio.sleep(artificial_delay_ms / 1000)

    result = dict(_MOCK_RESPONSE_TEMPLATE)
    result["processing_time_ms"] = round((time.perf_counter() - t_start) * 1000, 2)
    result["_mock_info"] = {
        "is_mock": True,
        "uploaded_file_size_kb": round(file_size_kb, 2),
        "artificial_delay_applied_ms": artificial_delay_ms or 0,
        "note": "Response ini TIDAK melalui inference AI — murni overhead backend",
    }

    return JSONResponse(content=result)


# ======================
# CONFIG (info mock)
# ======================
@router.get("/config")
def mock_config():
    return {
        "model": "MOCK — tidak ada model sungguhan",
        "purpose": "Kontrol eksperimen untuk membuktikan lokasi bottleneck (AI service vs backend)",
        "classes": ["kapsul", "softgel", "tablet"],
    }