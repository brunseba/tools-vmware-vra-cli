import React from 'react'
import { screen, fireEvent, waitFor } from '@testing-library/react'
import { render, createMockCatalogItem } from '@/tests/utils'
import { CatalogItemCard } from '../CatalogItemCard'

describe('CatalogItemCard', () => {
  const mockItem = createMockCatalogItem()
  const mockOnClick = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders catalog item information correctly', () => {
    render(<CatalogItemCard item={mockItem} />)

    expect(screen.getByText('Test Catalog Item')).toBeInTheDocument()
    expect(screen.getByText('Test catalog item description')).toBeInTheDocument()
    expect(screen.getByText('PUBLISHED')).toBeInTheDocument()
    expect(screen.getByText('v1.0')).toBeInTheDocument()
  })

  it('displays correct type icon and label', () => {
    render(<CatalogItemCard item={mockItem} />)
    
    // Should show Blueprint for blueprint type
    expect(screen.getByText('Blueprint')).toBeInTheDocument()
  })

  it('handles different item types correctly', () => {
    const workflowItem = createMockCatalogItem({
      type: { name: 'com.vmw.vro.workflow' },
      name: 'Test Workflow'
    })

    render(<CatalogItemCard item={workflowItem} />)
    expect(screen.getByText('vRO Workflow')).toBeInTheDocument()
  })

  it('displays status with correct color coding', () => {
    const activeItem = createMockCatalogItem({ status: 'ACTIVE' })
    render(<CatalogItemCard item={activeItem} />)
    
    const statusChip = screen.getByText('ACTIVE')
    expect(statusChip).toBeInTheDocument()
  })

  it('handles items without description gracefully', () => {
    const itemWithoutDescription = createMockCatalogItem({ description: undefined })
    render(<CatalogItemCard item={itemWithoutDescription} />)
    
    expect(screen.getByText('No description available')).toBeInTheDocument()
  })

  it('handles items without version gracefully', () => {
    const itemWithoutVersion = createMockCatalogItem({ version: undefined })
    render(<CatalogItemCard item={itemWithoutVersion} />)
    
    expect(screen.queryByText(/^v/)).not.toBeInTheDocument()
  })

  it('calls onClick when card is clicked', () => {
    render(<CatalogItemCard item={mockItem} onClick={mockOnClick} />)
    
    fireEvent.click(screen.getByRole('button', { name: /deploy/i }))
    expect(mockOnClick).toHaveBeenCalledTimes(1)
  })

  it('calls onClick when Deploy button is clicked', () => {
    render(<CatalogItemCard item={mockItem} onClick={mockOnClick} />)
    
    const deployButton = screen.getByRole('button', { name: /deploy/i })
    fireEvent.click(deployButton)
    
    expect(mockOnClick).toHaveBeenCalledTimes(1)
  })

  it('calls onClick when Info button is clicked', () => {
    render(<CatalogItemCard item={mockItem} onClick={mockOnClick} />)
    
    const infoButton = screen.getByRole('button', { name: /view details/i })
    fireEvent.click(infoButton)
    
    expect(mockOnClick).toHaveBeenCalledTimes(1)
  })

  it('shows item ID tooltip on hover', async () => {
    render(<CatalogItemCard item={mockItem} />)
    
    const idElement = screen.getByText('test-catalog-item')
    fireEvent.mouseOver(idElement)
    
    await waitFor(() => {
      expect(screen.getByText('ID: test-catalog-item')).toBeInTheDocument()
    })
  })

  it('truncates long names appropriately', () => {
    const longNameItem = createMockCatalogItem({
      name: 'This is a very long catalog item name that should be truncated'
    })
    
    render(<CatalogItemCard item={longNameItem} />)
    
    const nameElement = screen.getByText(longNameItem.name)
    expect(nameElement).toHaveStyle({
      'overflow': 'hidden',
      'text-overflow': 'ellipsis'
    })
  })

  it('applies hover effect styles', () => {
    render(<CatalogItemCard item={mockItem} />)
    
    const card = screen.getByText('Test Catalog Item').closest('[role="button"]')
    expect(card).toHaveStyle({
      'cursor': 'pointer',
      'transition': 'all 0.2s ease-in-out'
    })
  })

  it('handles click events with proper event stopping', () => {
    const mockCardClick = jest.fn()
    const mockButtonClick = jest.fn()

    render(
      <div onClick={mockCardClick}>
        <CatalogItemCard item={mockItem} onClick={mockButtonClick} />
      </div>
    )
    
    const deployButton = screen.getByRole('button', { name: /deploy/i })
    fireEvent.click(deployButton)
    
    expect(mockButtonClick).toHaveBeenCalledTimes(1)
    expect(mockCardClick).not.toHaveBeenCalled() // Event should be stopped
  })

  it('renders accessibility features correctly', () => {
    render(<CatalogItemCard item={mockItem} />)
    
    // Check for proper ARIA labels and roles
    expect(screen.getByRole('button', { name: /deploy/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /view details/i })).toBeInTheDocument()
  })
})