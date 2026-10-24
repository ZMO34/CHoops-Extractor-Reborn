"""Exercise a real native OpenGL context using only a synthetic triangle."""
from PySide6.QtWidgets import QApplication
from .scene_view import SceneView


def main():
    app = QApplication([])
    view = SceneView()
    view.resize(640, 480)
    view.set_meshes([{'name': 'synthetic', 'vertices': [
        (-1., 0., 0., 0., 0., 0., 0., 1.),
        (1., 0., 0., 1., 0., 0., 0., 1.),
        (0., 1., 0., .5, 1., 0., 0., 1.),
    ]}])
    view.show()
    for _ in range(20):
        app.processEvents()
    frame = view.grabFramebuffer()
    if not view.isValid() or view.error or frame.isNull():
        raise RuntimeError('Native OpenGL preview failed: '+view.error)
    view.close()
    app.processEvents()
    print('Native OpenGL context, shaders and framebuffer passed')
    return 0
