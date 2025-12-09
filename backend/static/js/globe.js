// globe.js
const container = document.getElementById("globe-container");

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 5000);
camera.position.set(0, 0, 350);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(container.clientWidth, container.clientHeight);
container.appendChild(renderer.domElement);

// Terre
const earth = new THREE.Mesh(
    new THREE.SphereGeometry(100, 64, 64),
    new THREE.MeshPhongMaterial({ color: 0x2266ff })
);
scene.add(earth);
scene.add(new THREE.AmbientLight(0xffffff, 1));

// Contrôles
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

// Resize
window.addEventListener("resize", () => {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
});

function animate() {
    requestAnimationFrame(animate);
    earth.rotation.y += 0.002;
    controls.update();
    renderer.render(scene, camera);
}
animate();
