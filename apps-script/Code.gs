/**
 * KPIs en acción · Backend (Google Apps Script + Google Sheets)
 * ------------------------------------------------------------
 * Este archivo va pegado en: Hoja de cálculo › Extensiones › Apps Script.
 * La hoja de cálculo debe tener tres pestañas:
 *   Claves  → Clave | ID | Nombre | Matrícula | Correo   (PRIVADA: nunca la subas a GitHub)
 *             Los alumnos entran con matrícula + correo; el docente con su clave DOC-.
 *   Equipos → ID | Nombre | Grupo | Equipo | Rol | Fecha   (la llena la página)
 *   Config  → Campo | Valor             (apertura y cierre)
 * Si alguna falta, ejecuta una vez la función prepararHoja().
 *
 * Todas las reglas se revisan aquí, en el servidor:
 *   · la clave debe existir en la hoja Claves;
 *   · cada estudiante solo puede estar en un equipo y solo en su grupo;
 *   · máximo 5 personas por equipo y un rol distinto por persona;
 *   · fuera del horario, solo el docente puede mover equipos.
 */

var ROLES = ['Coordinación y tiempo', 'Datos y semáforo', 'Ficha técnica', 'Plan de acción', 'Vocería'];
var MAX = 5, TEAMS = 5;

function doGet() {
  return json_({ ok: true, app: 'KPIs en acción', msg: 'El servicio está activo.' });
}

function doPost(e) {
  try {
    var req = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    var who = auth_(req.key);
    if (!who) return json_({ ok: false, error: 'Clave incorrecta.' });

    var a = req.action;
    if (a === 'login' || a === 'state') return json_(state_(who));

    var lock = LockService.getScriptLock();
    lock.waitLock(15000);
    try {
      var err = null;
      if (a === 'join') err = join_(who, +req.team, String(req.role || ''));
      else if (a === 'leave') err = leave_(who);
      else if (a === 'assign') err = assign_(who, String(req.rid || ''), +req.team);
      else if (a === 'schedule') err = schedule_(who, req.open, req.close);
      else err = 'Acción desconocida.';
      SpreadsheetApp.flush();
      var out = state_(who);
      if (err) { out.ok = false; out.error = err; }
      return json_(out);
    } finally {
      lock.releaseLock();
    }
  } catch (x) {
    return json_({ ok: false, error: 'Error del servidor: ' + x.message });
  }
}

/* ---------- Acciones ---------- */

function join_(who, team, role) {
  if (who.role !== 'alumno') return 'Usa el panel docente para asignar.';
  if (!(team >= 1 && team <= TEAMS)) return 'Equipo no válido.';
  if (ROLES.indexOf(role) < 0) return 'Elige tu rol.';
  if (!isOpen_()) return 'La actividad está cerrada según el horario.';
  var rows = signups_();
  var mine = rows.filter(function (r) { return r.rid === who.rid; })[0];
  if (mine) return 'Ya estás en el Equipo ' + mine.team + '.';
  var ms = rows.filter(function (r) { return r.g === who.g && r.team === team; });
  if (ms.length >= MAX) return 'Ese equipo ya está completo.';
  if (ms.some(function (r) { return r.role === role; })) return 'Ese rol ya está ocupado; elige otro.';
  sheet_('Equipos').appendRow([who.rid, who.name, who.g, team, role, new Date()]);
  return null;
}

function leave_(who) {
  if (who.role !== 'alumno') return 'Acción no válida.';
  if (!isOpen_()) return 'La actividad está cerrada; pide al docente que te mueva.';
  removeRow_(who.rid);
  return null;
}

function assign_(who, rid, team) {
  if (who.role !== 'docente') return 'Solo el docente puede asignar.';
  var c = claves_().filter(function (k) { return k.id === rid; })[0];
  if (!c) return 'Estudiante no encontrado.';
  var g = rid.charAt(0);
  if (!team) { removeRow_(rid); return null; }
  if (!(team >= 1 && team <= TEAMS)) return 'Equipo no válido.';
  var ms = signups_().filter(function (r) { return r.g === g && r.team === team && r.rid !== rid; });
  if (ms.length >= MAX) return 'El Equipo ' + team + ' ya tiene 5 integrantes.';
  var role = ROLES.filter(function (r) { return !ms.some(function (x) { return x.role === r; }); })[0];
  removeRow_(rid);
  sheet_('Equipos').appendRow([rid, c.name, g, team, role, new Date()]);
  return null;
}

function schedule_(who, open, close) {
  if (who.role !== 'docente') return 'Solo el docente puede editar el horario.';
  var o = Date.parse(open), c = Date.parse(close);
  if (!o || !c || c <= o) return 'Elige una apertura y un cierre posterior.';
  var sh = sheet_('Config');
  sh.getRange(1, 1, 3, 2).setValues([['Campo', 'Valor'], ['open', new Date(o).toISOString()], ['close', new Date(c).toISOString()]]);
  return null;
}

/* ---------- Lectura ---------- */

function state_(who) {
  var ks = claves_(), roster = { L: [], A: [] };
  ks.forEach(function (k) {
    if (k.role !== 'alumno') return;
    if (who.role === 'docente' || k.g === who.g) roster[k.g][k.idx] = k.name;
  });
  return {
    ok: true,
    me: { role: who.role, rid: who.rid || null, g: who.g || null, name: who.name },
    roster: roster,
    signups: signups_().map(function (r) { return { rid: r.rid, g: r.g, team: r.team, role: r.role, ts: r.ts }; })
      .filter(function (r) { return who.role === 'docente' || r.g === who.g; }),
    schedule: getSchedule_(),
    now: Date.now()
  };
}

function auth_(raw) {
  var s = String(raw || '').trim(), ks = claves_();
  var m = s.match(/^M:(\d+)\|(.+@.+)$/);
  if (m) {
    var mat = m[1].replace(/^0+/, ''), mail = m[2].toLowerCase();
    return ks.filter(function (k) { return k.mat && k.mat === mat && k.mail === mail; })[0] || null;
  }
  var key = s.toUpperCase().replace(/[^A-Z0-9-]/g, '');
  if (!key) return null;
  return ks.filter(function (k) { return k.key === key; })[0] || null;
}

function claves_() {
  var cache = CacheService.getScriptCache(), hit = cache.get('claves');
  if (hit) return JSON.parse(hit);
  var v = sheet_('Claves').getDataRange().getValues().slice(1), out = [];
  v.forEach(function (r) {
    var key = String(r[0]).trim().toUpperCase(), id = String(r[1]).trim(), name = String(r[2]).trim();
    var mat = String(r[3] || '').replace(/\D/g, '').replace(/^0+/, ''), mail = String(r[4] || '').trim().toLowerCase();
    if (!id) return;
    if (id === 'DOC') out.push({ key: key, id: 'DOC', role: 'docente', name: name || 'Docente' });
    else {
      var m = id.match(/^([LA]):(\d+)$/);
      if (m) out.push({ key: key, id: id, rid: id, g: m[1], idx: +m[2], role: 'alumno', name: name, mat: mat, mail: mail });
    }
  });
  cache.put('claves', JSON.stringify(out), 300);
  return out;
}

function signups_() {
  var v = sheet_('Equipos').getDataRange().getValues().slice(1);
  return v.filter(function (r) { return r[0]; }).map(function (r) {
    return { rid: String(r[0]), g: String(r[2]), team: +r[3], role: String(r[4]), ts: r[5] instanceof Date ? r[5].getTime() : Date.parse(r[5]) || 0 };
  });
}

function removeRow_(rid) {
  var sh = sheet_('Equipos'), v = sh.getDataRange().getValues();
  for (var i = v.length - 1; i >= 1; i--) if (String(v[i][0]) === rid) sh.deleteRow(i + 1);
}

function getSchedule_() {
  var v = sheet_('Config').getDataRange().getValues(), s = {};
  v.forEach(function (r) { if (r[0] === 'open' || r[0] === 'close') s[r[0]] = r[1] instanceof Date ? r[1].toISOString() : String(r[1]); });
  return s.open && s.close ? s : null;
}

function isOpen_() {
  var s = getSchedule_();
  if (!s) return true; // sin horario definido: abierta
  var n = Date.now();
  return n >= Date.parse(s.open) && n <= Date.parse(s.close);
}

/* ---------- Utilidades ---------- */

function sheet_(name) {
  var sh = SpreadsheetApp.getActive().getSheetByName(name);
  if (!sh) throw new Error('Falta la pestaña «' + name + '». Ejecuta prepararHoja().');
  return sh;
}

function json_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

/** Ejecútala una vez si falta alguna pestaña. No borra datos existentes. */
function prepararHoja() {
  var ss = SpreadsheetApp.getActive();
  [['Claves', ['Clave', 'ID', 'Nombre', 'Matrícula', 'Correo']], ['Equipos', ['ID', 'Nombre', 'Grupo', 'Equipo', 'Rol', 'Fecha']], ['Config', ['Campo', 'Valor']]]
    .forEach(function (d) {
      var sh = ss.getSheetByName(d[0]) || ss.insertSheet(d[0]);
      if (!sh.getRange(1, 1).getValue()) sh.getRange(1, 1, 1, d[1].length).setValues([d[1]]).setFontWeight('bold');
    });
  CacheService.getScriptCache().remove('claves');
}

/** Si cambias claves o nombres en la hoja, ejecútala para que se apliquen al momento. */
function limpiarCache() {
  CacheService.getScriptCache().remove('claves');
}
