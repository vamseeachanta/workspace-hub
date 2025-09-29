import React, { useRef, useEffect } from 'react';
import * as d3 from 'd3';

interface HeatmapDataPoint {
  x: string;
  y: string;
  value: number;
}

interface HeatmapProps {
  data: HeatmapDataPoint[];
  width?: number;
  height?: number;
  colorScheme?: string[];
  className?: string;
}

export function Heatmap({
  data,
  width = 800,
  height = 400,
  colorScheme = ['#f0f9ff', '#0ea5e9', '#0369a1'],
  className = ''
}: HeatmapProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!data || data.length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const margin = { top: 40, right: 100, bottom: 60, left: 80 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const container = svg
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Get unique x and y values
    const xValues = Array.from(new Set(data.map(d => d.x))).sort();
    const yValues = Array.from(new Set(data.map(d => d.y))).sort();

    // Scales
    const xScale = d3.scaleBand()
      .domain(xValues)
      .range([0, innerWidth])
      .padding(0.1);

    const yScale = d3.scaleBand()
      .domain(yValues)
      .range([0, innerHeight])
      .padding(0.1);

    const colorScale = d3.scaleSequential()
      .interpolator(d3.interpolateRgbBasis(colorScheme))
      .domain(d3.extent(data, d => d.value) as [number, number]);

    // Create heatmap cells
    const cells = container
      .selectAll('.heatmap-cell')
      .data(data)
      .enter()
      .append('rect')
      .attr('class', 'heatmap-cell')
      .attr('x', d => xScale(d.x) || 0)
      .attr('y', d => yScale(d.y) || 0)
      .attr('width', xScale.bandwidth())
      .attr('height', yScale.bandwidth())
      .attr('fill', d => colorScale(d.value))
      .attr('rx', 4)
      .attr('ry', 4);

    // Add hover effects and tooltips
    cells
      .on('mouseover', function(event, d) {
        d3.select(this)
          .transition()
          .duration(200)
          .attr('stroke', 'hsl(var(--foreground))')
          .attr('stroke-width', 2);

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
              <div class="font-medium">${d.x} - ${d.y}</div>
              <div class="text-muted-foreground">Value: ${d.value.toFixed(2)}</div>
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
          .attr('stroke', 'none');

        d3.selectAll('.tooltip')
          .transition()
          .duration(200)
          .style('opacity', 0)
          .remove();
      });

    // Add axes
    const xAxis = d3.axisBottom(xScale);
    const yAxis = d3.axisLeft(yScale);

    container
      .append('g')
      .attr('class', 'axis')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(xAxis)
      .selectAll('text')
      .style('text-anchor', 'end')
      .attr('dx', '-.8em')
      .attr('dy', '.15em')
      .attr('transform', 'rotate(-45)');

    container
      .append('g')
      .attr('class', 'axis')
      .call(yAxis);

    // Add color legend
    const legendWidth = 20;
    const legendHeight = 200;
    const legendX = innerWidth + 20;
    const legendY = (innerHeight - legendHeight) / 2;

    const legendScale = d3.scaleLinear()
      .domain(colorScale.domain())
      .range([legendHeight, 0]);

    const legendAxis = d3.axisRight(legendScale)
      .tickSize(6)
      .tickFormat(d3.format('.1f'));

    // Create gradient for legend
    const defs = svg.append('defs');
    const gradient = defs.append('linearGradient')
      .attr('id', 'heatmap-gradient')
      .attr('gradientUnits', 'userSpaceOnUse')
      .attr('x1', 0).attr('y1', legendHeight)
      .attr('x2', 0).attr('y2', 0);

    const numStops = 10;
    for (let i = 0; i <= numStops; i++) {
      const value = colorScale.domain()[0] + (i / numStops) * (colorScale.domain()[1] - colorScale.domain()[0]);
      gradient.append('stop')
        .attr('offset', `${(i / numStops) * 100}%`)
        .attr('stop-color', colorScale(value));
    }

    // Add legend rectangle
    container
      .append('rect')
      .attr('x', legendX)
      .attr('y', legendY)
      .attr('width', legendWidth)
      .attr('height', legendHeight)
      .style('fill', 'url(#heatmap-gradient)')
      .attr('rx', 4)
      .attr('ry', 4);

    // Add legend axis
    container
      .append('g')
      .attr('class', 'axis')
      .attr('transform', `translate(${legendX + legendWidth}, ${legendY})`)
      .call(legendAxis);

    // Animation
    cells
      .style('opacity', 0)
      .transition()
      .delay((d, i) => i * 20)
      .duration(500)
      .style('opacity', 1);

  }, [data, width, height, colorScheme]);

  return (
    <div className={`d3-chart ${className}`}>
      <svg ref={svgRef} />
    </div>
  );
}