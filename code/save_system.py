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


def _save_path() -> str:
	base_dir = os.path.dirname(os.path.abspath(__file__))
	return os.path.join(base_dir, SAVE_FILENAME)


def _slot_path(slot: int) -> str:
	base_dir = os.path.dirname(os.path.abspath(__file__))
	s = int(slot)
	return os.path.join(base_dir, SLOT_TEMPLATE.format(slot=s))


def _config_path() -> str:
	base_dir = os.path.dirname(os.path.abspath(__file__))
	return os.path.join(base_dir, CONFIG_FILENAME)


def save_exists() -> bool:
	return os.path.exists(_save_path())


def slot_exists(slot: int) -> bool:
	path = _slot_path(slot)
	if os.path.exists(path):
		return True
	# Legacy single save is treated as slot 1 if slot1 doesn't exist
	return int(slot) == 1 and os.path.exists(_save_path())


def list_slots():
	return list(range(1, SLOT_COUNT + 1))


def config_exists() -> bool:
	return os.path.exists(_config_path())


def delete_save() -> None:
	try:
		os.remove(_save_path())
	except FileNotFoundError:
		pass


def delete_slot(slot: int) -> None:
	try:
		os.remove(_slot_path(slot))
	except FileNotFoundError:
		pass


def delete_config() -> None:
	try:
		os.remove(_config_path())
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
	payload = {
		'version': SAVE_VERSION,
		'timestamp': int(time.time()),
		'data': data,
	}
	text = json.dumps(payload, ensure_ascii=False, indent=2)
	_atomic_write_text(_save_path(), text)


def save_game_slot(slot: int, data: Dict[str, Any]) -> None:
	s = int(slot)
	if s < 1 or s > SLOT_COUNT:
		raise ValueError('Invalid save slot')
	payload = {
		'version': SAVE_VERSION,
		'timestamp': int(time.time()),
		'data': data,
	}
	text = json.dumps(payload, ensure_ascii=False, indent=2)
	_atomic_write_text(_slot_path(s), text)


def load_game() -> Optional[Dict[str, Any]]:
	path = _save_path()
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
	# Legacy support: if slot1 doesn't exist, use savegame.json
	if not os.path.exists(path) and s == 1 and os.path.exists(_save_path()):
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
		# Legacy support for slot1
		if s == 1 and os.path.exists(_save_path()):
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
	payload = {
		'version': CONFIG_VERSION,
		'timestamp': int(time.time()),
		'data': data,
	}
	text = json.dumps(payload, ensure_ascii=False, indent=2)
	_atomic_write_text(_config_path(), text)


def load_settings() -> Optional[Dict[str, Any]]:
	path = _config_path()
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
