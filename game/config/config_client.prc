# Default window properties...
window-title Cog Invasion Online (Alpha)
win-origin -1 -1
win-size 640 480
load-display pandadx9
aux-display pandagl

# Logging...
notify-level warning
default-directnotify-level warning

# Filenames...
cursor-filename toonmono.cur
icon-filename icon.ico

default-model-extension .egg

model-cache-model #t
model-cache-textures #t

model-path .

# Audio...

# Woo-hoo!!!! Miles!!
audio-library-name p3miles_audio

# Virtual file system...
vfs-mount phase_3.mf /
vfs-mount phase_3.5.mf /
vfs-mount phase_4.mf /
vfs-mount phase_5.mf /
vfs-mount phase_5.5.mf /
vfs-mount phase_6.mf /
vfs-mount phase_7.mf /
vfs-mount phase_8.mf /
vfs-mount phase_9.mf /
vfs-mount phase_10.mf /
vfs-mount phase_11.mf /
vfs-mount phase_12.mf /
vfs-mount phase_13.mf /

# Server...
server-port 7032
server-address gameserver.coginvasion.com

# Performance...
hardware-animated-vertices #f
sync-video #f
smooth-lag 0.2
basic-shaders-only #f
framebuffer-multisample 1
multisamples 16

# Game content...
game-name Cog Invasion
want-weapons #t
want-pies #t
want-chat #t
want-sa-reactions #f
gag-start-key delete
gag-throw-key delete-up
want-firstperson-battle #f

want-pstats 0

egg-load-old-curves 0
