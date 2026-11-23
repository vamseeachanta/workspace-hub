import React, { useRef, useEffect } from 'react';
import * as d3 from 'd3';

interface DataPoint {
  timestamp: Date;
  value: number;
}

interface LineChartProps {
  data: DataPoint[];
  width?: number;
  height?: number;
  color?: string;
  showArea?: boolean;
  showDots?: boolean;
  showGrid?: boolean;
  animate?: boolean;
  className?: string;
}

export function LineChart({
  data,
  width = 800,
  height = 400,
  color = '#3B82F6',
  showArea = false,
  showDots = true,
  showGrid = true,
  animate = true,
  className = ''
}: LineChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!data || data.length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const margin = { top: 20, right: 30, bottom: 40, left: 40 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const container = svg
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Scales
    const xScale = d3.scaleTime()
      .domain(d3.extent(data, d => d.timestamp) as [Date, Date])
      .range([0, innerWidth]);

    const yScale = d3.scaleLinear()
      .domain(d3.extent(data, d => d.value) as [number, number])
      .nice()
      .range([innerHeight, 0]);

    // Grid
    if (showGrid) {
      // Horizontal grid lines
      container.append('g')
        .attr('class', 'grid')
        .selectAll('line')
        .data(yScale.ticks())
        .enter()
        .append('line')
        .attr('x1', 0)
        .attr('x2', innerWidth)
        .attr('y1', d => yScale(d))
        .attr('y2', d => yScale(d))
        .attr('stroke', 'currentColor')
        .attr('stroke-opacity', 0.1);

      // Vertical grid lines
      container.append('g')
        .attr('class', 'grid')
        .selectAll('line')
        .data(xScale.ticks())
        .enter()
        .append('line')
        .attr('x1', d => xScale(d))
        .attr('x2', d => xScale(d))
        .attr('y1', 0)
        .attr('y2', innerHeight)
        .attr('stroke', 'currentColor')
        .attr('stroke-opacity', 0.1);
    }

    // Line generator
    const line = d3.line<DataPoint>()
      .x(d => xScale(d.timestamp))
      .y(d => yScale(d.value))
      .curve(d3.curveMonotoneX);

    // Area generator
    const area = d3.area<DataPoint>()
      .x(d => xScale(d.timestamp))
      .y0(innerHeight)
      .y1(d => yScale(d.value))
      .curve(d3.curveMonotoneX);

    // Add area if enabled
    if (showArea) {
      const areaPath = container
        .append('path')
        .datum(data)
        .attr('class', 'area')
        .attr('d', area)
        .attr('fill', color)
        .attr('fill-opacity', 0.2);

      if (animate) {
        areaPath
          .attr('opacity', 0)
          .transition()
          .duration(1000)
          .attr('opacity', 1);
      }
    }

    // Add line
    const linePath = container
      .append('path')
      .datum(data)
      .attr('class', 'line')
      .attr('d', line)
      .attr('fill', 'none')
      .attr('stroke', color)
      .attr('stroke-width', 2);

    if (animate) {
      const totalLength = linePath.node()?.getTotalLength() || 0;
      linePath
        .attr('stroke-dasharray', `${totalLength} ${totalLength}`)
        .attr('stroke-dashoffset', totalLength)
        .transition()
        .duration(1500)
        .ease(d3.easeLinear)
        .attr('stroke-dashoffset', 0);
    }

    // Add dots
    if (showDots) {
      const dots = container
        .selectAll('.dot')
        .data(data)
        .enter()
        .append('circle')
        .attr('class', 'dot')
        .attr('cx', d => xScale(d.timestamp))
        .attr('cy', d => yScale(d.value))
        .attr('r', 4)
        .attr('fill', color)
        .attr('stroke', '#fff')
        .attr('stroke-width', 2);

      if (animate) {
        dots
          .attr('r', 0)
          .transition()
          .delay((d, i) => i * 50)
          .duration(300)
          .attr('r', 4);
      }

      // Add hover effects
      dots
        .on('mouseover', function(event, d) {
          d3.select(this)
            .transition()
            .duration(200)
            .attr('r', 6);

          // Tooltip
          const tooltip = d3.select('body')
            .append('div')
            .attr('class', 'tooltip')
            .style('opacity', 0)
            .style('position', 'absolute')
            .style('background', 'hsl(var(--popover))')
            .style('color', 'hsl(var(--popover-foreground))')
            .style('border', '1px solid hsl(var(--border))')
            .style('border-radius', '6px')
            .style('padding', '8px 12px')
            .style('font-size', '12px')
            .style('pointer-events', 'none')
            .style('z-index', '9999');

          tooltip
            .html(`
              <div>
                <div class="font-medium">${d.value.toFixed(2)}</div>
                <div class="text-muted-foreground">${d.timestamp.toLocaleString()}</div>
              </div>
            `)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 10) + 'px')
            .transition()
            .duration(200)
            .style('opacity', 1);
        })
        .on('mouseout', function() {
          d3.select(this)
            .transition()
            .duration(200)
            .attr('r', 4);

          d3.selectAll('.tooltip')
            .transition()
            .duration(200)
            .style('opacity', 0)
            .remove();
        });
    }

    // Axes
    const xAxis = d3.axisBottom(xScale)
      .tickFormat(d3.timeFormat('%H:%M'));

    const yAxis = d3.axisLeft(yScale);

    container
      .append('g')
      .attr('class', 'axis')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(xAxis);

    container
      .append('g')
      .attr('class', 'axis')
      .call(yAxis);

  }, [data, width, height, color, showArea, showDots, showGrid, animate]);

  return (
    <div className={`d3-chart ${className}`}>
      <svg ref={svgRef} />
    </div>
  );
}