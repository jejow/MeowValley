import json
import os
import time
from typing import Any, Dict, Optional


SAVE_VERSION = 1
SAVE_FILENAME = 'savegame.json'

SLOT_COUNT = 5
SLOT_TEMPLATE = 'save_slot_{slot}.json'

CONFIG_VERSION = 1
CONFIG_FILENAME = 'config.json'


def _project_root() -> str:
	"""Return project root (folder containing `code/`)."""
	return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))


def _save_dir() -> str:
	"""Directory where all saves/config are stored."""
	return os.path.join(_project_root(), 'savegame')


def _ensure_save_dir() -> None:
	try:
		os.makedirs(_save_dir(), exist_ok=True)
	except Exception:
		# If we can't create the folder, we'll fall back to legacy paths.
		pass


def _read_bytes(path: str) -> Optional[bytes]:
	try:
		with open(path, 'rb') as f:
			return f.read()
	except Exception:
		return None


def _safe_migrate_file(src: str, dst: str) -> bool:
	"""Move src -> dst safely.

	- If dst doesn't exist: move.
	- If dst exists and content matches: delete src.
	- If dst exists and differs: move src to dst with `.legacy.<timestamp>` suffix.

	Returns True if src was removed (moved or deleted).
	"""
	if not os.path.exists(src):
		return False
	try:
		os.makedirs(os.path.dirname(dst), exist_ok=True)
	except Exception:
		return False

	if not os.path.exists(dst):
		try:
			os.replace(src, dst)
			return True
		except Exception:
			return False

	# dst exists: compare content best-effort
	src_bytes = _read_bytes(src)
	dst_bytes = _read_bytes(dst)
	if src_bytes is not None and dst_bytes is not None and src_bytes == dst_bytes:
		try:
			os.remove(src)
			return True
		except Exception:
			return False

	stamp = int(time.time())
	legacy_dst = f"{dst}.legacy.{stamp}"
	try:
		os.replace(src, legacy_dst)
		return True
	except Exception:
		return False


def migrate_legacy_saves() -> Dict[str, Any]:
	"""Migrate any legacy saves/config from `code/` into `savegame/`.

	This is safe to run multiple times.
	"""
	_ensure_save_dir()

	results = {
		'migrated': [],
		'skipped': [],
	}

	# single save + config
	legacy_pairs = [
		(_legacy_save_path(), _save_path()),
		(_legacy_config_path(), _config_path()),
	]
	for src, dst in legacy_pairs:
		if os.path.exists(src):
			if _safe_migrate_file(src, dst):
				results['migrated'].append({'from': src, 'to': dst})
			else:
				results['skipped'].append({'from': src, 'to': dst})

	# slot saves
	for slot in list_slots():
		src = _legacy_slot_path(slot)
		dst = _slot_path(slot)
		if os.path.exists(src):
			if _safe_migrate_file(src, dst):
				results['migrated'].append({'from': src, 'to': dst})
			else:
				results['skipped'].append({'from': src, 'to': dst})

	return results


def _save_path() -> str:
	# New location: project_root/savegame/
	return os.path.join(_save_dir(), SAVE_FILENAME)


def _legacy_save_path() -> str:
	# Old location: code/
	base_dir = os.path.dirname(os.path.abspath(__file__))
	return os.path.join(base_dir, SAVE_FILENAME)


def _slot_path(slot: int) -> str:
	s = int(slot)
	return os.path.join(_save_dir(), SLOT_TEMPLATE.format(slot=s))


def _legacy_slot_path(slot: int) -> str:
	base_dir = os.path.dirname(os.path.abspath(__file__))
	s = int(slot)
	return os.path.join(base_dir, SLOT_TEMPLATE.format(slot=s))


def _config_path() -> str:
	return os.path.join(_save_dir(), CONFIG_FILENAME)


def _legacy_config_path() -> str:
	base_dir = os.path.dirname(os.path.abspath(__file__))
	return os.path.join(base_dir, CONFIG_FILENAME)


def save_exists() -> bool:
	return os.path.exists(_save_path()) or os.path.exists(_legacy_save_path())


def slot_exists(slot: int) -> bool:
	# New location
	if os.path.exists(_slot_path(slot)):
		return True
	# Legacy location
	if os.path.exists(_legacy_slot_path(slot)):
		return True
	# Legacy single save is treated as slot 1 if slot1 doesn't exist
	return int(slot) == 1 and os.path.exists(_legacy_save_path())


def list_slots():
	return list(range(1, SLOT_COUNT + 1))


def config_exists() -> bool:
	return os.path.exists(_config_path()) or os.path.exists(_legacy_config_path())


def delete_save() -> None:
	for p in (_save_path(), _legacy_save_path()):
		try:
			os.remove(p)
		except FileNotFoundError:
			pass


def delete_slot(slot: int) -> None:
	for p in (_slot_path(slot), _legacy_slot_path(slot)):
		try:
			os.remove(p)
		except FileNotFoundError:
			pass


def delete_config() -> None:
	for p in (_config_path(), _legacy_config_path()):
		try:
			os.remove(p)
		except FileNotFoundError:
			pass


def _atomic_write_text(path: str, text: str) -> None:
	tmp_path = path + '.tmp'
	with open(tmp_path, 'w', encoding='utf-8') as f:
		f.write(text)
		f.flush()
		os.fsync(f.fileno())
	os.replace(tmp_path, path)


def save_game(data: Dict[str, Any]) -> None:
	_ensure_save_dir()
	payload = {
		'version': SAVE_VERSION,
		'timestamp': int(time.time()),
		'data': data,
	}
	text = json.dumps(payload, ensure_ascii=False, indent=2)
	try:
		_atomic_write_text(_save_path(), text)
	except Exception:
		# Fall back to legacy location if the save dir isn't writable.
		_atomic_write_text(_legacy_save_path(), text)


def save_game_slot(slot: int, data: Dict[str, Any]) -> None:
	s = int(slot)
	if s < 1 or s > SLOT_COUNT:
		raise ValueError('Invalid save slot')
	_ensure_save_dir()
	payload = {
		'version': SAVE_VERSION,
		'timestamp': int(time.time()),
		'data': data,
	}
	text = json.dumps(payload, ensure_ascii=False, indent=2)
	try:
		_atomic_write_text(_slot_path(s), text)
	except Exception:
		_atomic_write_text(_legacy_slot_path(s), text)


def load_game() -> Optional[Dict[str, Any]]:
	path = _save_path()
	if not os.path.exists(path):
		path = _legacy_save_path()
		if not os.path.exists(path):
			return None
	try:
		with open(path, 'r', encoding='utf-8') as f:
			payload = json.load(f)
	except Exception:
		return None

	if not isinstance(payload, dict):
		return None
	if payload.get('version') != SAVE_VERSION:
		# For now we only support version 1.
		return None

	data = payload.get('data')
	return data if isinstance(data, dict) else None


def load_game_slot(slot: int) -> Optional[Dict[str, Any]]:
	s = int(slot)
	if s < 1 or s > SLOT_COUNT:
		return None
	path = _slot_path(s)
	if not os.path.exists(path):
		path = _legacy_slot_path(s)
	# Legacy support: if slot1 doesn't exist, use savegame.json
	if not os.path.exists(path) and s == 1 and save_exists():
		return load_game()
	if not os.path.exists(path):
		return None
	try:
		with open(path, 'r', encoding='utf-8') as f:
			payload = json.load(f)
	except Exception:
		return None

	if not isinstance(payload, dict):
		return None
	if payload.get('version') != SAVE_VERSION:
		return None

	data = payload.get('data')
	return data if isinstance(data, dict) else None


def _load_slot_meta(slot: int) -> Optional[Dict[str, Any]]:
	s = int(slot)
	path = _slot_path(s)
	if not os.path.exists(path):
		path = _legacy_slot_path(s)
	if not os.path.exists(path):
		# Legacy support for slot1 single-save
		if s == 1 and os.path.exists(_legacy_save_path()):
			path = _legacy_save_path()
		elif s == 1 and os.path.exists(_save_path()):
			path = _save_path()
		else:
			return None
	try:
		with open(path, 'r', encoding='utf-8') as f:
			payload = json.load(f)
	except Exception:
		return None
	return payload if isinstance(payload, dict) else None


def slot_summary(slot: int) -> Dict[str, Any]:
	meta = _load_slot_meta(slot)
	if not meta:
		return {'exists': False}
	return {
		'exists': True,
		'timestamp': meta.get('timestamp'),
	}


def format_slot_label(slot: int) -> str:
	info = slot_summary(slot)
	if not info.get('exists'):
		return f'Slot {slot}: Kosong'
	try:
		ts = int(info.get('timestamp') or 0)
		if ts <= 0:
			return f'Slot {slot}: Ada'
		# Local time string
		stamp = time.strftime('%Y-%m-%d %H:%M', time.localtime(ts))
		return f'Slot {slot}: {stamp}'
	except Exception:
		return f'Slot {slot}: Ada'


def save_settings(data: Dict[str, Any]) -> None:
	_ensure_save_dir()
	payload = {
		'version': CONFIG_VERSION,
		'timestamp': int(time.time()),
		'data': data,
	}
	text = json.dumps(payload, ensure_ascii=False, indent=2)
	try:
		_atomic_write_text(_config_path(), text)
	except Exception:
		_atomic_write_text(_legacy_config_path(), text)


def load_settings() -> Optional[Dict[str, Any]]:
	path = _config_path()
	if not os.path.exists(path):
		path = _legacy_config_path()
		if not os.path.exists(path):
			return None
	try:
		with open(path, 'r', encoding='utf-8') as f:
			payload = json.load(f)
	except Exception:
		return None

	if not isinstance(payload, dict):
		return None
	if payload.get('version') != CONFIG_VERSION:
		return None

	data = payload.get('data')
	return data if isinstance(data, dict) else None
