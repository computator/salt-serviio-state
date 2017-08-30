{% set version = salt['cp.get_url']("http://update.serviio.org/releases.xml", None).split('linux', 1)[1].split('version=', 2)[1].split('"', 2)[1] %}

java:
  pkg.installed:
    - name: default-jre-headless

ffmpeg-static:
  archive.extracted:
    - name: /opt/ffmpeg
    - source: https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-{% if grains['osarch'] == "amd64" %}64{% else %}32{% endif %}bit-static.tar.xz
    - source_hash: https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-{% if grains['osarch'] == "amd64" %}64{% else %}32{% endif %}bit-static.tar.xz.md5
    - keep: true
    - clean: true
    - options: --strip-components 1
    - enforce_toplevel: false

dcraw:
  pkg.installed: []

serviio-files:
  archive.extracted:
    - name: /opt/serviio
    - source: http://download.serviio.org/releases/serviio-{{ version }}-linux.tar.gz
    - skip_verify: true
    - keep: true
    - clean: true
    - options: --strip-components 1
    - enforce_toplevel: false
    - user: root
    - group: root
  file.replace:
    - name: /opt/serviio/config/log4j.xml
    - pattern: <param name="File" value="\$\{serviio.home\}/log/serviio.log" />
    - repl: <param name="File" value="/var/log/serviio/serviio.log" />
    - require:
      - archive: serviio-files

serviio:
  file.managed:
    - name: /usr/local/lib/systemd/system/serviio.service
    - source: salt://serviio/serviio.service
    - makedirs: true
    - require:
      - archive: serviio-files
      - file: serviio-files
      - archive: ffmpeg-static
      - pkg: dcraw
      - pkg: java
  service.running:
    - enable: true
    - require:
      - file: serviio