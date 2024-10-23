// ParkingCanvas.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';

function calculateMiddlePoint(points) {
  const totalPoints = points.length;
  let sumX = 0;
  let sumY = 0;

  points.forEach(point => {
    sumX += point[0];
    sumY += point[1];
  });

  const middleX = sumX / totalPoints;
  const middleY = sumY / totalPoints;

  return [middleX, middleY];
}

const ParkingCanvas = () => {
  const [parkingData, setParkingData] = useState([]);
  const [parkingSlotsData, setParkingSlotsData] = useState(
    {
      "coords": [],
      "occupancy": [],
      "name": []
    }
  );

  useEffect(() => {
    // Fetch parking coordinates from Django Rest API
    axios.get('http://localhost:8000/api/parking_coords/119')
      .then(response => {
        setParkingData(response.data['coords']);
      })
      .catch(error => {
        console.error('Error fetching parking data:', error);
      });
  }, []);

  useEffect(() => {
    // Fetch parking slots' coordinates from Django Rest API
    axios.get('http://localhost:8000/api/parking_slots_coords/119')
      .then(response => {
        setParkingSlotsData(response.data);
      })
      .catch(error => {
        console.error('Error fetching parking data:', error);
      });
  }, []);

  function drawParking(mouseX=null, mouseY=null){
    const canvas = document.getElementById('parkingCanvas');
    const ctx = canvas.getContext('2d');
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw parking shapes using coordinates
    parkingData.forEach((shape, index) => {
      ctx.beginPath();
      ctx.moveTo(shape[0][0], shape[0][1]);

      for (let i = 1; i < shape.length; i++) {
        ctx.lineTo(shape[i][0], shape[i][1]);
      }

      ctx.lineWidth = 3;
      ctx.setLineDash([]);
      ctx.strokeStyle ='rgba(20, 150, 0, 1)';
      ctx.stroke();
    });

    // Draw parking slots' shapes on the canvas
    parkingSlotsData['coords'].forEach((shape, index) => {
      ctx.beginPath();
      ctx.moveTo(shape[0][0], shape[0][1]);

      for (let i = 1; i < shape.length; i++) {
        ctx.lineTo(shape[i][0], shape[i][1]);
      }

      ctx.closePath();
      ctx.lineWidth = 2;
      ctx.setLineDash([10, 5]);
      if (parkingSlotsData['occupancy'][index]){
        ctx.strokeStyle = 'rgba(150, 0, 0, 0.5)';
        ctx.stroke();
        ctx.fillStyle = 'rgba(150, 0, 0, 0.2)';
        ctx.fill();
      }
      else {
        ctx.strokeStyle = 'rgba(20, 150, 10, 0.5)';
        ctx.stroke();
        if (ctx.isPointInPath(mouseX, mouseY)){
          if (!parkingSlotsData['occupancy'][index]){
            ctx.fillStyle = 'rgba(20, 150, 10, 0.2)';
            ctx.fill();
          }
        }
      }

      // Adding text in the middle of the shape
      const middlePoint = calculateMiddlePoint(shape);
      const text = parkingSlotsData["name"][index];
      ctx.font = '14px Arial';
      ctx.fillStyle = 'black';
      ctx.textAlign = 'center';
      ctx.fillText(text, middlePoint[0], middlePoint[1]);
    });
  }

  useEffect(() => {
    const canvas = document.getElementById('parkingCanvas');
    const ctx = canvas.getContext('2d');

    const handleMouseMove = (event) => {
      const rect = canvas.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      drawParking(x, y);
    };

    canvas.addEventListener('mousemove', handleMouseMove);

    return () => {
      canvas.removeEventListener('mousemove', handleMouseMove);
    };
  }, [parkingSlotsData]);

  useEffect(() => {
     drawParking();

  }, [parkingData, parkingSlotsData]);

  return (
    <canvas
      id="parkingCanvas"
      width={1900}
      height={800}
    ></canvas>
  );
};

export default ParkingCanvas;
