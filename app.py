from flask import Flask, request, jsonify
from flask_cors import CORS
import xml.etree.ElementTree as ET
import heapq
import math
from typing import Dict, List, Tuple, Optional
import json
#holaaaaa
app = Flask(__name__)
CORS(app)  # Permitir CORS para desarrollo

class Graph:
    def __init__(self):
        self.nodes = {}  # id -> (lat, lon)
        self.edges = {}  # (node1, node2) -> weight
        self.adjacency = {}  # node -> [neighbors]
    
    def add_node(self, node_id: int, lat: float, lon: float):
        self.nodes[node_id] = (lat, lon)
        if node_id not in self.adjacency:
            self.adjacency[node_id] = []
    
    def add_edge(self, node1: int, node2: int, weight: float):
        if node1 not in self.adjacency:
            self.adjacency[node1] = []
        if node2 not in self.adjacency:
            self.adjacency[node2] = []
        
        self.adjacency[node1].append(node2)
        self.adjacency[node2].append(node1)
        self.edges[(node1, node2)] = weight
        self.edges[(node2, node1)] = weight
    
    def get_edge_weight(self, node1: int, node2: int) -> float:
        return self.edges.get((node1, node2), float('inf'))
    
    def get_neighbors(self, node: int) -> List[int]:
        return self.adjacency.get(node, [])

class CampusRouter:
    def __init__(self, osm_file_path: str):
        self.graph = Graph()
        self.load_osm_data(osm_file_path)
    
    def load_osm_data(self, osm_file_path: str):
        """Carga los datos del archivo OSM y construye el grafo"""
        try:
            tree = ET.parse(osm_file_path)
            root = tree.getroot()
            
            # Primero cargar todos los nodos
            for node in root.findall('.//node'):
                node_id = int(node.get('id'))
                lat = float(node.get('lat'))
                lon = float(node.get('lon'))
                self.graph.add_node(node_id, lat, lon)
            
            # Luego cargar las vías (ways) que conectan nodos
            for way in root.findall('.//way'):
                # Solo procesar vías que sean caminos transitables
                way_tags = {tag.get('k'): tag.get('v') for tag in way.findall('tag')}
                
                # Filtrar solo caminos transitables
                highway_types = ['path', 'footway', 'pedestrian', 'residential', 'service', 'unclassified']
                if way_tags.get('highway') in highway_types:
                    nodes = [int(nd.get('ref')) for nd in way.findall('nd')]
                    
                    # Crear aristas entre nodos consecutivos
                    for i in range(len(nodes) - 1):
                        node1, node2 = nodes[i], nodes[i + 1]
                        if node1 in self.graph.nodes and node2 in self.graph.nodes:
                            weight = self.calculate_distance(node1, node2)
                            self.graph.add_edge(node1, node2, weight)
            
            print(f"Grafo cargado: {len(self.graph.nodes)} nodos, {len(self.graph.edges)//2} aristas")
            
        except Exception as e:
            print(f"Error cargando archivo OSM: {e}")
    
    def calculate_distance(self, node1_id: int, node2_id: int) -> float:
        """Calcula la distancia euclidiana entre dos nodos"""
        if node1_id not in self.graph.nodes or node2_id not in self.graph.nodes:
            return float('inf')
        
        lat1, lon1 = self.graph.nodes[node1_id]
        lat2, lon2 = self.graph.nodes[node2_id]
        
        # Fórmula de Haversine para distancia real
        R = 6371000  # Radio de la Tierra en metros
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def find_nearest_node(self, lat: float, lon: float) -> Optional[int]:
        """Encuentra el nodo más cercano a las coordenadas dadas"""
        if not self.graph.nodes:
            return None
        
        min_distance = float('inf')
        nearest_node = None
        
        for node_id, (node_lat, node_lon) in self.graph.nodes.items():
            distance = self.calculate_distance_coords(lat, lon, node_lat, node_lon)
            if distance < min_distance:
                min_distance = distance
                nearest_node = node_id
        
        return nearest_node
    
    def calculate_distance_coords(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcula distancia entre coordenadas"""
        R = 6371000
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def dijkstra(self, start_node: int, end_node: int) -> Tuple[List[int], float]:
        """Implementación del algoritmo de Dijkstra"""
        if start_node not in self.graph.nodes or end_node not in self.graph.nodes:
            return [], float('inf')
        
        distances = {node: float('inf') for node in self.graph.nodes}
        distances[start_node] = 0
        previous = {}
        pq = [(0, start_node)]
        
        while pq:
            current_distance, current_node = heapq.heappop(pq)
            
            if current_node == end_node:
                break
            
            if current_distance > distances[current_node]:
                continue
            
            for neighbor in self.graph.get_neighbors(current_node):
                weight = self.graph.get_edge_weight(current_node, neighbor)
                distance = current_distance + weight
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_node
                    heapq.heappush(pq, (distance, neighbor))
        
        # Reconstruir el camino
        path = []
        current = end_node
        while current in previous:
            path.append(current)
            current = previous[current]
        path.append(start_node)
        path.reverse()
        
        return path, distances[end_node]
    
    def astar(self, start_node: int, end_node: int) -> Tuple[List[int], float]:
        """Implementación del algoritmo A*"""
        if start_node not in self.graph.nodes or end_node not in self.graph.nodes:
            return [], float('inf')
        
        def heuristic(node: int) -> float:
            """Heurística: distancia euclidiana al objetivo"""
            if node not in self.graph.nodes or end_node not in self.graph.nodes:
                return float('inf')
            lat1, lon1 = self.graph.nodes[node]
            lat2, lon2 = self.graph.nodes[end_node]
            return self.calculate_distance_coords(lat1, lon1, lat2, lon2)
        
        distances = {node: float('inf') for node in self.graph.nodes}
        distances[start_node] = 0
        previous = {}
        pq = [(0 + heuristic(start_node), 0, start_node)]
        
        while pq:
            f_score, current_distance, current_node = heapq.heappop(pq)
            
            if current_node == end_node:
                break
            
            if current_distance > distances[current_node]:
                continue
            
            for neighbor in self.graph.get_neighbors(current_node):
                weight = self.graph.get_edge_weight(current_node, neighbor)
                distance = current_distance + weight
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_node
                    f_score = distance + heuristic(neighbor)
                    heapq.heappush(pq, (f_score, distance, neighbor))
        
        # Reconstruir el camino
        path = []
        current = end_node
        while current in previous:
            path.append(current)
            current = previous[current]
        path.append(start_node)
        path.reverse()
        
        return path, distances[end_node]

# Instancia global del router
campus_router = None

@app.route('/load-osm', methods=['POST'])
def load_osm():
    """Endpoint para cargar el archivo OSM"""
    global campus_router
    
    try:
        data = request.get_json()
        osm_file_path = data.get('osm_file_path')
        
        if not osm_file_path:
            return jsonify({'success': False, 'message': 'Ruta del archivo OSM no proporcionada'})
        
        campus_router = CampusRouter(osm_file_path)
        return jsonify({
            'success': True, 
            'message': f'OSM cargado exitosamente. {len(campus_router.graph.nodes)} nodos, {len(campus_router.graph.edges)//2} aristas'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error cargando OSM: {str(e)}'})

@app.route('/calculate-route', methods=['POST'])
def calculate_route():
    """Endpoint para calcular la ruta más corta"""
    global campus_router
    
    if campus_router is None:
        return jsonify({'success': False, 'message': 'OSM no cargado. Use /load-osm primero'})
    
    try:
        data = request.get_json()
        start_lat = data['startPoint']['latitude']
        start_lon = data['startPoint']['longitude']
        end_lat = data['endPoint']['latitude']
        end_lon = data['endPoint']['longitude']
        algorithm = data.get('algorithm', 'dijkstra')
        
        # Encontrar nodos más cercanos
        start_node = campus_router.find_nearest_node(start_lat, start_lon)
        end_node = campus_router.find_nearest_node(end_lat, end_lon)
        
        if start_node is None or end_node is None:
            return jsonify({'success': False, 'message': 'No se pudieron encontrar nodos cercanos'})
        
        # Calcular ruta
        if algorithm == 'astar':
            path, distance = campus_router.astar(start_node, end_node)
        else:
            path, distance = campus_router.dijkstra(start_node, end_node)
        
        if not path:
            return jsonify({'success': False, 'message': 'No se encontró ruta entre los puntos'})
        
        # Convertir nodos a coordenadas
        route_points = []
        for node_id in path:
            lat, lon = campus_router.graph.nodes[node_id]
            route_points.append({
                'lat': lat,
                'lon': lon,
                'name': f'Nodo {node_id}',
                'description': f'Punto de la ruta'
            })
        
        return jsonify({
            'success': True,
            'route': route_points,
            'distance': distance,
            'duration': int(distance / 1.4),  # Estimación: 1.4 m/s caminando
            'message': f'Ruta calculada usando {algorithm}'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error calculando ruta: {str(e)}'})

@app.route('/graph-info', methods=['GET'])
def graph_info():
    """Endpoint para obtener información del grafo"""
    global campus_router
    
    if campus_router is None:
        return jsonify({'success': False, 'message': 'OSM no cargado'})
    
    return jsonify({
        'success': True,
        'nodes_count': len(campus_router.graph.nodes),
        'edges_count': len(campus_router.graph.edges) // 2,
        'bounds': {
            'min_lat': min(lat for lat, lon in campus_router.graph.nodes.values()),
            'max_lat': max(lat for lat, lon in campus_router.graph.nodes.values()),
            'min_lon': min(lon for lat, lon in campus_router.graph.nodes.values()),
            'max_lon': max(lon for lat, lon in campus_router.graph.nodes.values())
        }
    })

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de salud"""
    return jsonify({'status': 'OK', 'message': 'Servidor funcionando correctamente'})

if __name__ == '__main__':
    import os
    default_osm_path = 'campus.osm'
    if os.path.exists(default_osm_path):
        print(f"Cargando OSM desde {default_osm_path}...")
        campus_router = CampusRouter(default_osm_path)
        print("OSM cargado exitosamente")
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port) 
